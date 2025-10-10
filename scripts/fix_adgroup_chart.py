#!/usr/bin/env python3
"""
Diagnose and optionally fix Ad Group Performance chart column mismatch.

Default expectation: chart 257 uses dataset 29 and groups by `ad_group_name`.

Usage (diagnose only):
  SUPERSET_BASE_URL=http://localhost:8088 \
  SUPERSET_USERNAME=admin \
  SUPERSET_PASSWORD=admin \
  python scripts/fix_adgroup_chart.py --chart-id 257 --dataset-id 29 --expected-column ad_group_name

If dataset column differs, replace in chart params:
  python scripts/fix_adgroup_chart.py \
    --chart-id 257 --dataset-id 29 \
    --expected-column ad_group_name \
    --replace-with adgroup_name
"""
import argparse
import json
import sys
from typing import Any, Dict, List

from superset_tools.api_client import SupersetClient, SupersetConfig


def collect_column_names(ds: Dict[str, Any]) -> List[str]:
    cols = ds.get("columns") or []
    names: List[str] = []
    for c in cols:
        # GET dataset may return nested structure per column
        n = c.get("column_name") or c.get("name") or c.get("verbose_name")
        if n:
            names.append(n)
    return names


def replace_in_params(params: Dict[str, Any], old: str, new: str) -> Dict[str, Any]:
    # Replace in common fields where dimensions are declared
    changed = False

    def repl_list(key: str):
        nonlocal changed
        if key in params and isinstance(params[key], list):
            params[key] = [new if v == old else v for v in params[key]]
            changed = True

    def repl_str(key: str):
        nonlocal changed
        if key in params and isinstance(params[key], str) and params[key] == old:
            params[key] = new
            changed = True

    repl_list("groupby")
    repl_list("columns")
    repl_list("all_columns")
    repl_str("x")
    repl_str("y")

    # Also replace adhoc filters if present
    if "adhoc_filters" in params and isinstance(params["adhoc_filters"], list):
        for f in params["adhoc_filters"]:
            if isinstance(f, dict):
                if f.get("column") and isinstance(f["column"], dict):
                    if f["column"].get("column_name") == old:
                        f["column"]["column_name"] = new
                        changed = True
                # SQL expression fallback
                if f.get("subject") == old:
                    f["subject"] = new
                    changed = True

    if not changed:
        return params
    return params


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chart-id", type=int, required=True)
    parser.add_argument("--dataset-id", type=int, required=True)
    parser.add_argument("--expected-column", type=str, default="ad_group_name")
    parser.add_argument("--replace-with", type=str, default=None)
    args = parser.parse_args()

    client = SupersetClient(SupersetConfig())
    client.login()

    print("Syncing dataset columns from source…")
    try:
        client.refresh_dataset(args.dataset_id)
    except Exception as e:
        print(f"Warning: dataset refresh failed: {e}")

    ds = client.get_dataset(args.dataset_id)
    cols = collect_column_names(ds)
    print(f"Dataset {args.dataset_id} has {len(cols)} columns.")

    if args.expected_column in cols:
        print(f"OK: '{args.expected_column}' exists in dataset.")
    else:
        print(f"Missing column: '{args.expected_column}' not found in dataset columns.")
        similar = [c for c in cols if c.lower().replace(" ", "") in {
            "adgroupname", "ad_group_name", "segmentsadgroupname", "ad_group"} or "ad_group" in c.lower()]
        if similar:
            print("Potential alternatives in dataset:")
            for c in sorted(set(similar)):
                print(f" - {c}")
        else:
            print("No obvious alternatives found.")

    chart = client.get_chart(args.chart_id)
    params_raw = chart.get("params") or "{}"
    try:
        params = json.loads(params_raw)
    except Exception:
        print("Error: chart params are not valid JSON.")
        return 1

    # If replace-with provided and expected column is missing, update chart params
    if args.replace_with and args.expected_column not in cols:
        new_params = replace_in_params(params, args.expected_column, args.replace_with)
        if new_params != params:
            payload = {
                "params": json.dumps(new_params),
                "dataset_id": args.dataset_id,
                "query_context": chart.get("query_context"),
                "owners": [o["id"] if isinstance(o, dict) else o for o in chart.get("owners", [])],
                "slice_name": chart.get("slice_name"),
                "viz_type": chart.get("viz_type"),
                "cache_timeout": chart.get("cache_timeout"),
                "description": chart.get("description"),
            }
            client.update_chart(args.chart_id, payload)
            print(
                f"Updated chart {args.chart_id}: replaced '{args.expected_column}' with '{args.replace_with}'."
            )
        else:
            print("No changes made to chart params.")
    else:
        print("Diagnosis complete. Re-run with --replace-with <column> to update chart if needed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

