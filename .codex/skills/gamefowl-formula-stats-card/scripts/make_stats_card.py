#!/usr/bin/env python3
import argparse
from pathlib import Path

METRICS = [
    "Focus / alertness",
    "Energy availability",
    "Fatigue/stress tolerance",
    "Fast recovery",
    "ATP regeneration",
    "Anti-inflammatory / antioxidant support",
    "Respiratory / acid-base support",
    "Hydration / electrolyte balance",
    "GI tolerance",
    "Onset speed",
    "Shelf stability / commercial readiness",
]


def card(name: str) -> str:
    rows = "\n".join(f"| {m} | /10 |  |  |  |" for m in METRICS)
    return f"""# {name} — Formula Stats Card

## Formula stats card

| Metric | Score | Confidence | Key drivers | Limiting factors |
|---|---:|---|---|---|
{rows}

## Ingredient contribution matrix

Notation: `++` strong positive, `+` modest positive, `0` neutral, `-` risk, `--` blocker, `?` unknown.

| Ingredient | Focus | Energy | Fatigue | Recovery | ATP | Antiox | Resp | Hydration | GI | Onset | Shelf | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |  |

## Rollups

- Performance-support score: /10
- Recovery/welfare score: /10
- Commercial-readiness score: /10

## Interpretation

### Top strengths
1. 
2. 
3. 

### Bottlenecks
1. 
2. 
3. 

### Next validation
- 
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--formula", default="Formula")
    ap.add_argument("--out", default="stats-card.md")
    args = ap.parse_args()
    Path(args.out).write_text(card(args.formula), encoding="utf-8")
    print(Path(args.out).resolve())

if __name__ == "__main__":
    main()
