
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def create_ga_kpi_users():
    """
    Creates a Big Number chart for Total Users from dataset 33.
    """
    client = SupersetClient()
    client.login()

    datasource_id = 33
    slice_name = "GA: Total Users"

    params = {
        "datasource": f"{datasource_id}__table",
        "viz_type": "big_number_total",
        "metric": "users",
        "adhoc_filters": [
            {
                "clause": "WHERE",
                "subject": "event_date_parsed",
                "operator": "TEMPORAL_RANGE",
                "comparator": "Last 90 days",
                "expressionType": "SIMPLE"
            }
        ],
        "y_axis_format": ",.0f", # Format as a whole number
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
    create_ga_kpi_users()
