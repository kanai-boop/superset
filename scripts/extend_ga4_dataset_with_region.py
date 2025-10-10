#!/usr/bin/env python3
"""
Extend a GA4 virtual dataset SQL to include geo.region as geo_region
and update GROUP BY accordingly.

By default operates on dataset ID 30.

Usage:
  SUPERSET_BASE_URL=http://localhost:8088 \
  SUPERSET_USERNAME=admin \
  SUPERSET_PASSWORD=admin \
  python scripts/extend_ga4_dataset_with_region.py --dataset-id 30 --dry-run

  Remove --dry-run to apply the change.
"""
import argparse
import json
import re
import sys
from typing import Optional

from superset_tools.api_client import SupersetClient, SupersetConfig


def propose_sql_with_region(sql: str) -> Optional[str]:
    # If already contains geo_region alias, do nothing
    if re.search(r"\bgeo_region\b", sql, re.IGNORECASE):
        return None

    # Insert `, geo.region as geo_region` before FROM
    m = re.search(r"\bFROM\b", sql, re.IGNORECASE)
    if not m:
        return None
    insert_pos = m.start()
    new_select = sql[:insert_pos].rstrip()
    rest = sql[insert_pos:]

    # Ensure preceding comma
    if not new_select.rstrip().endswith(","):
        new_select = new_select + ","
    new_select = new_select + " geo.region as geo_region "

    new_sql = new_select + rest

    # Append geo_region to GROUP BY list
    g = re.search(r"\bGROUP\s+BY\b\s*([^;]+)$", new_sql, re.IGNORECASE)
    if g:
        gb_expr = g.group(1).strip()
        if gb_expr.endswith(";"):
            gb_expr = gb_expr[:-1]
        if not re.search(r"\bgeo_region\b", gb_expr, re.IGNORECASE):
            gb_expr = gb_expr + ", geo_region"
        new_sql = new_sql[: g.start()] + f"GROUP BY {gb_expr}"
    else:
        # No GROUP BY; not expected for aggregated query, but add it conservatively
        new_sql = new_sql.rstrip(" ;") + " GROUP BY geo_region"

    return new_sql


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = SupersetClient(SupersetConfig())
    client.login()

    ds = client.get_dataset(args.dataset_id)
    if (ds.get("kind") or "").lower() != "virtual":
        print(f"Dataset {args.dataset_id} is not a virtual dataset; aborting.")
        return 1

    sql = ds.get("sql") or ""
    if not sql:
        print("No SQL found on dataset; aborting.")
        return 1

    proposed = propose_sql_with_region(sql)
    if proposed is None:
        print("geo_region already present or could not compute modification.")
        return 0

    if args.dry_run:
        print("--- Current SQL ---")
        print(sql)
        print("\n--- Proposed SQL (with geo_region) ---")
        print(proposed)
        return 0

    payload = {"sql": proposed}
    client._request("PUT", f"/api/v1/dataset/{args.dataset_id}", json=payload)
    # Refresh columns so geo_region is registered
    try:
        client.refresh_dataset(args.dataset_id)
    except Exception:
        pass
    print(f"Updated dataset {args.dataset_id} to include geo_region and refreshed columns.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

