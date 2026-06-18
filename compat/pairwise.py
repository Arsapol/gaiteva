"""Pairwise incompatibility matrix evaluator.

The registry is a Tier-0 practical reactivity screen.  It is intentionally
separate from :mod:`compat.gibbs`: Gibbs thermodynamics may be reported as a
backup explanation, but pairwise rule hits are the primary gate for practical
stored-product incompatibility.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any, Iterable, cast

_REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "substances"
    / "compatibility"
    / "pairwise-rules.json"
)
_DEFAULT_SEVERITY_ORDER = ["pass", "advisory", "marginal", "block", "unknown"]
_KNOWN_CONTEXTS = {
    "dry",
    "wet_stored",
    "make_fresh",
    "concentrate",
    "reconstituted_drink",
    "oil_emulsion",
    "capsule_premix",
}


def load_registry(path: str | Path | None = None) -> dict[str, Any]:
    """Load the versioned pairwise rule registry from disk.

    Uses a path relative to this module, not ``Path.cwd()``, so smoke scripts can
    call it from any working directory.
    """
    registry_path = Path(path) if path is not None else _REGISTRY_PATH
    with registry_path.open("r", encoding="utf-8") as handle:
        registry = json.load(handle)
    validate_registry(registry)
    return registry


def validate_registry(registry: dict[str, Any]) -> None:
    """Minimal built-in schema validation for the rule registry.

    The project has no required JSON-schema dependency, so this catches the
    fields the evaluator relies on and keeps CI/smoke validation dependency-free.
    """
    required_top = {"schema_version", "severity_order", "substance_classes", "rules"}
    missing_top = required_top - registry.keys()
    if missing_top:
        raise ValueError(f"pairwise registry missing top-level fields: {sorted(missing_top)}")
    severity_rank = _severity_rank(registry)
    if not isinstance(registry["rules"], list) or not registry["rules"]:
        raise ValueError("pairwise registry must contain at least one rule")
    for rule in registry["rules"]:
        missing = {
            "rule_id",
            "status",
            "a",
            "b",
            "phase_contexts",
            "mechanism",
            "severity",
            "confidence",
            "mitigations",
            "validation",
            "source_refs",
        } - rule.keys()
        if missing:
            raise ValueError(f"rule {rule.get('rule_id', '<unknown>')} missing fields: {sorted(missing)}")
        if rule["severity"] not in severity_rank:
            raise ValueError(f"rule {rule['rule_id']} has invalid severity {rule['severity']!r}")
        for context, downgraded in rule.get("downgrade_contexts", {}).items():
            if downgraded not in severity_rank:
                raise ValueError(f"rule {rule['rule_id']} downgrade for {context!r} has invalid severity {downgraded!r}")
        for side in ("a", "b"):
            selector = rule[side]
            if not isinstance(selector, dict) or not ({"key", "class"} & selector.keys()):
                raise ValueError(f"rule {rule['rule_id']} selector {side} must include key or class")


def _component_key(component: str | tuple[str, float] | dict[str, Any]) -> str:
    if isinstance(component, str):
        return component.strip().lower()
    if isinstance(component, tuple):
        return str(component[0]).strip().lower()
    for field in ("key", "name", "ingredient", "substance"):
        if field in component:
            return str(component[field]).strip().lower()
    raise ValueError(f"component cannot be resolved to a substance key: {component!r}")


def _classes_for(key: str, class_map: dict[str, list[str]], extra_classes: dict[str, list[str]] | None) -> set[str]:
    classes = set(class_map.get(key, []))
    if extra_classes and key in extra_classes:
        classes.update(extra_classes[key])
    return classes


def _selector_matches(selector: dict[str, str], key: str, classes: set[str]) -> bool:
    if "key" in selector and selector["key"] != key:
        return False
    if "class" in selector and selector["class"] not in classes:
        return False
    return True


def _rule_matches(rule: dict[str, Any], left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        _selector_matches(rule["a"], left["key"], left["classes"])
        and _selector_matches(rule["b"], right["key"], right["classes"])
    ) or (
        _selector_matches(rule["a"], right["key"], right["classes"])
        and _selector_matches(rule["b"], left["key"], left["classes"])
    )


def _contextual_severity(rule: dict[str, Any], context: str) -> tuple[str, str]:
    if context in rule.get("phase_contexts", []):
        return rule["severity"], "direct"
    downgraded = rule.get("downgrade_contexts", {}).get(context)
    if downgraded:
        return downgraded, "mitigated-by-context"
    return "pass", "out-of-scope-context"


def _severity_rank(registry: dict[str, Any] | None = None) -> dict[str, int]:
    order = list((registry or {}).get("severity_order") or _DEFAULT_SEVERITY_ORDER)
    if "pass" not in order:
        order.insert(0, "pass")
    return {severity: index for index, severity in enumerate(order)}


def _max_severity(values: Iterable[str], registry: dict[str, Any] | None = None) -> str:
    rank = _severity_rank(registry)
    return max(values, key=lambda severity: rank.get(severity, -1), default="pass")


def _overall_severity(known_severities: list[str], has_unknowns: bool, registry: dict[str, Any]) -> str:
    max_known = _max_severity(known_severities, registry)
    # Known blockers should remain visible to callers that gate on overall_severity.
    # Unknown coverage is reported separately via has_unknowns/unmodeled_pairs.
    if max_known == "block":
        return "block"
    if has_unknowns:
        return "unknown"
    return max_known


def evaluate_pairwise(
    components: list[str | tuple[str, float] | dict[str, Any]],
    phase_context: str,
    *,
    registry: dict[str, Any] | None = None,
    extra_classes: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Evaluate pairwise incompatibility rules for a formula.

    Parameters
    ----------
    components:
        Substance keys, ``(key, grams)`` tuples, or dicts containing ``key`` or
        ``name``.
    phase_context:
        One of ``dry``, ``wet_stored``, ``make_fresh``, ``concentrate``,
        ``reconstituted_drink``, ``oil_emulsion``, or ``capsule_premix``.
    registry:
        Optional pre-loaded registry.  If omitted, the bundled JSON registry is
        loaded and minimally validated.
    extra_classes:
        Optional caller-supplied classes for new/experimental substances.

    Returns
    -------
    dict containing a normalized hit ledger, unknown substances, unmodeled pairs,
    and an overall severity.  Unmodeled pairs are explicit unknowns, never silent
    passes.
    """
    if phase_context not in _KNOWN_CONTEXTS:
        raise ValueError(f"unknown phase_context {phase_context!r}; expected {sorted(_KNOWN_CONTEXTS)}")

    active_registry = registry or load_registry()
    class_map = cast(dict[str, list[str]], active_registry["substance_classes"])
    keys = list(dict.fromkeys(_component_key(component) for component in components))
    enriched: list[dict[str, Any]] = [
        {"key": key, "classes": _classes_for(key, class_map, extra_classes)}
        for key in keys
    ]

    unknown_substances = sorted(item["key"] for item in enriched if not item["classes"])
    rule_hits: list[dict[str, Any]] = []
    unmodeled_pairs: list[dict[str, Any]] = []

    for left, right in itertools.combinations(enriched, 2):
        matched_rules = [
            rule for rule in active_registry["rules"]
            if rule.get("status") == "active" and _rule_matches(rule, left, right)
        ]
        if not matched_rules:
            unmodeled_pairs.append({
                "pair": [left["key"], right["key"]],
                "severity": "unknown",
                "reason": "no active pairwise rule matched this exact/class pair",
            })
            continue
        contextual_hits = []
        out_of_scope_rule_ids = []
        for rule in matched_rules:
            severity, applicability = _contextual_severity(rule, phase_context)
            if severity == "pass" and applicability == "out-of-scope-context":
                out_of_scope_rule_ids.append(rule["rule_id"])
                continue
            contextual_hits.append((rule, severity, applicability))
        if not contextual_hits:
            unmodeled_pairs.append({
                "pair": [left["key"], right["key"]],
                "severity": "unknown",
                "reason": "matched rules do not model this phase_context",
                "phase_context": phase_context,
                "matched_rule_ids": out_of_scope_rule_ids,
            })
            continue
        for rule, severity, applicability in contextual_hits:
            rule_hits.append({
                "pair": [left["key"], right["key"]],
                "rule_id": rule["rule_id"],
                "mechanism": rule["mechanism"],
                "severity": severity,
                "base_severity": rule["severity"],
                "confidence": rule["confidence"],
                "applicability": applicability,
                "mitigations": rule.get("mitigations", []),
                "validation": rule.get("validation", []),
                "source_refs": rule.get("source_refs", []),
            })

    known_severities = [hit["severity"] for hit in rule_hits if hit["severity"] != "unknown"]
    has_unknowns = bool(unknown_substances or unmodeled_pairs)

    return {
        "schema_version": active_registry["schema_version"],
        "phase_context": phase_context,
        "component_count": len(keys),
        "components": keys,
        "rule_hits": rule_hits,
        "unknown_substances": unknown_substances,
        "unmodeled_pairs": unmodeled_pairs,
        "has_unknowns": has_unknowns,
        "max_known_severity": _max_severity(known_severities, active_registry),
        "overall_severity": _overall_severity(known_severities, has_unknowns, active_registry),
        "gibbs_role": "backup-only explanation; not a primary compatibility gate",
    }


def format_pairwise_report(report: dict[str, Any]) -> str:
    """Return a compact human-readable pairwise compatibility report."""
    lines = [
        "Pairwise incompatibility report",
        f"Context: {report['phase_context']}",
        f"Overall severity: {report['overall_severity']}",
        f"Gibbs role: {report['gibbs_role']}",
    ]
    if report["rule_hits"]:
        lines.append("Rule hits:")
        for hit in report["rule_hits"]:
            pair = " + ".join(hit["pair"])
            lines.append(
                f"- {hit['severity'].upper()} {pair}: {hit['rule_id']} "
                f"({hit['mechanism']})"
            )
    if report["unknown_substances"]:
        lines.append("Unknown substances: " + ", ".join(report["unknown_substances"]))
    if report["unmodeled_pairs"]:
        lines.append(f"Unmodeled pairs: {len(report['unmodeled_pairs'])} explicit unknown(s)")
    return "\n".join(lines)


if __name__ == "__main__":
    demo = evaluate_pairwise(
        ["d_ribose", "ascorbic_acid", "l_tyrosine", "copper_tbcc"],
        "wet_stored",
    )
    print(format_pairwise_report(demo))
