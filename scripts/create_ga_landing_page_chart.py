
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def create_ga_landing_page_chart():
    """
    Creates a Table chart for Top 10 Landing Pages from dataset 30.
    """
    client = SupersetClient()
    client.login()

    datasource_id = 30
    slice_name = "GA: Top 10 Landing Pages"

    params = {
        "datasource": f"{datasource_id}__table",
        "viz_type": "table",
        "groupby": ["landing_page"],
        "metrics": ["sessions", "users"],
        "all_columns": ["landing_page", "sessions", "users"],
        "row_limit": 10,
        "adhoc_filters": [],
        "orderby": [["sessions", False]], # Sort by sessions descending
        "table_timestamp_format": "smart_date",
        "show_cell_bars": True,
    }

    payload = {
        "slice_name": slice_name,
        "viz_type": params["viz_type"],
        "datasource_id": datasource_id,
        "datasource_type": "table",
        "params": json.dumps(params),
    }

    print(f"Creating chart for '{slice_name}'...")
    try:
        resp = client._request("POST", "/api/v1/chart/", json=payload)
        chart_id = resp.json()["id"]
        print(f"Successfully created chart '{slice_name}' with ID: {chart_id}")
        return chart_id
    except Exception as e:
        print(f"!!! Failed to create chart '{slice_name}': {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    create_ga_landing_page_chart()
