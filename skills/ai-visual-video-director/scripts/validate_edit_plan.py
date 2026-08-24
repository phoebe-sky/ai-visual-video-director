#!/usr/bin/env python3
"""Validate an AI Visual Video Director edit plan without third-party schema packages."""

import argparse, json, sys
from pathlib import Path

STRATEGIES={
"presenter_only","kinetic_typography","number_card","comparison","chart","diagram",
"timeline","checklist","ui_card","icon","logo","screenshot","picture_in_picture",
"b_roll","visual_metaphor","generated_visual"
}

def validate(plan):
    errors=[]
    cues=plan.get("visual_cues")
    if not isinstance(cues,list):
        return ["visual_cues must be an array"]
    last_start=-1.0
    for i,c in enumerate(cues):
        prefix=f"visual_cues[{i}]"
        for key in ("start_time","end_time","visual_strategy"):
            if key not in c: errors.append(f"{prefix}.{key} is required")
        try:
            start=float(c.get("start_time",0)); end=float(c.get("end_time",0))
            if start<0 or end<=start: errors.append(f"{prefix} has invalid time range")
            if start<last_start: errors.append(f"{prefix} is not in chronological order")
            last_start=start
        except (TypeError,ValueError):
            errors.append(f"{prefix} times must be numeric")
        strategy=c.get("visual_strategy")
        if strategy not in STRATEGIES: errors.append(f"{prefix}.visual_strategy unsupported: {strategy}")
        if strategy=="chart":
            data=c.get("data") or {}
            labels=data.get("labels") or []; values=data.get("values") or []
            if not labels or len(labels)!=len(values):
                errors.append(f"{prefix} chart requires equal non-empty labels and values")
        if strategy in {"screenshot","picture_in_picture","b_roll","logo"} and c.get("asset_path"):
            if not Path(c["asset_path"]).expanduser().exists():
                errors.append(f"{prefix}.asset_path does not exist: {c['asset_path']}")
    return errors

def main():
    p=argparse.ArgumentParser()
    p.add_argument("plan")
    args=p.parse_args()
    path=Path(args.plan)
    plan=json.loads(path.read_text(encoding="utf-8"))
    errors=validate(plan)
    result={"valid":not errors,"errors":errors,"visual_cues":len(plan.get("visual_cues",[]))}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if not errors else 2

if __name__=="__main__":
    raise SystemExit(main())
