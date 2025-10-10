#!/usr/bin/env python3
"""
Add a Region native filter to a dashboard by updating json_metadata.

Usage:
  SUPERSET_BASE_URL=http://localhost:8088 \
  SUPERSET_USERNAME=admin \
  SUPERSET_PASSWORD=admin \
  python scripts/add_region_filter.py \
    --dashboard-id 13 \
    --name "Region" \
    --dataset 27:segments_geo_region \
    --dataset 29:geo_region \

Notes:
  - Pass one or more --dataset <id>:<column> pairs to target Ads and GA4 datasets.
  - Script preserves existing filters and dashboard layout.
"""
import argparse
import json
import sys
import uuid
from typing import List, Tuple

from superset_tools.api_client import SupersetClient, SupersetConfig


def parse_dataset_arg(arg: str) -> Tuple[int, str]:
    try:
        ds, col = arg.split(":", 1)
        return int(ds), col
    except Exception:
        raise argparse.ArgumentTypeError(
            f"Invalid --dataset value '{arg}', expected format <id>:<column>"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dashboard-id", type=int, required=True)
    parser.add_argument("--name", type=str, default="Region")
    parser.add_argument(
        "--dataset", action="append", type=parse_dataset_arg, default=[],
        help="Target pair <dataset_id>:<column_name>. Repeat to add multiple targets.")
    parser.add_argument(
        "--filter-type", type=str, default="filter_select",
        help="Native filter type, e.g. filter_select, filter_range."
    )
    args = parser.parse_args()

    client = SupersetClient(SupersetConfig())
    client.login()

    dash = client.get_dashboard(args.dashboard_id)
    # GET returns owners as objects; for update, pass owner IDs
    owner_ids = [o["id"] if isinstance(o, dict) else o for o in dash.get("owners", [])]

    # Parse json_metadata
    jm_raw = dash.get("json_metadata") or "{}"
    try:
        jm = json.loads(jm_raw)
    except Exception:
        jm = {}

    nfc: List[dict] = jm.get("native_filter_configuration") or []

    filter_id = f"NATIVE_FILTER-{uuid.uuid4()}"
    targets = [
        {"datasetId": ds_id, "column": {"name": col_name}}
        for (ds_id, col_name) in args.dataset
    ]

    region_filter = {
        "id": filter_id,
        "name": args.name,
        "filterType": args.filter_type,
        "targets": targets,
        "defaultDataMask": {},
        "cascadeParentIds": [],
        "scope": {"rootPath": [], "excluded": []},
        "controlValues": {"enableEmptyFilter": True},
    }

    nfc.append(region_filter)
    jm["native_filter_configuration"] = nfc

    payload = {
        "dashboard_title": dash.get("dashboard_title"),
        "slug": dash.get("slug"),
        "owners": owner_ids,
        "position_json": dash.get("position_json"),
        "json_metadata": json.dumps(jm),
        "css": dash.get("css"),
        "published": dash.get("published", True),
    }

    client.update_dashboard(args.dashboard_id, payload)
    print(
        f"Added native filter '{args.name}' with {len(targets)} target(s) to dashboard {args.dashboard_id}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

