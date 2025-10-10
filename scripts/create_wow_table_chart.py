
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def create_wow_table_chart():
    """
    Creates a table chart showing Week-over-Week changes for key metrics.
    """
    client = SupersetClient()
    client.login()

    datasource_id = 31
    slice_name = "WoW Performance Snapshot"

    params = {
        "datasource": f"{datasource_id}__table",
        "viz_type": "table",
        "groupby": ["campaign_base_campaign"],
        "metrics": ["cost", "conversions", "cpa", "roas"],
        "time_grain_sqla": "P1W",
        "time_range": "Last 90 days", # A time range is required for time comparison
        "compare_lag": "1",
        "comparison_type": "percentage",
        "time_compare": ["1 week ago"],
        "row_limit": 100,
        "series_limit": 0,
        "percent_metrics": ["roas", "cpa"], # Ensure these are formatted as percentages if needed
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
    create_wow_table_chart()
