
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def create_ga_traffic_source_chart():
    """
    Creates a Pie chart for Top 5 Traffic Sources from dataset 30.
    """
    client = SupersetClient()
    client.login()

    datasource_id = 30
    slice_name = "GA: Top 5 Traffic Sources"

    params = {
        "datasource": f"{datasource_id}__table",
        "viz_type": "pie",
        "groupby": ["traffic_medium"],
        "metric": "sessions",
        "row_limit": 5,
        "adhoc_filters": [], # No time filter needed for this overall view
        "show_legend": True,
        "show_labels": True,
        "labels_outside": True,
        "label_type": "key_value_percent",
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
    create_ga_traffic_source_chart()
