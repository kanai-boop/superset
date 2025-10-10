
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def create_hourly_trend_chart():
    """
    Creates an Hourly Performance Trend line chart using dataset 32.
    """
    client = SupersetClient()
    client.login()

    datasource_id = 32
    slice_name = "Hourly Performance Trend"

    params = {
        "datasource": f"{datasource_id}__table",
        "viz_type": "echarts_timeseries_line",
        "x_axis": "hour",
        "metrics": ["clicks"],
        "adhoc_filters": [
            {
                "clause": "WHERE",
                "subject": "date",
                "operator": "TEMPORAL_RANGE",
                "comparator": "No filter",
                "expressionType": "SIMPLE"
            }
        ],
        "row_limit": 10000,
        "groupby": [], # No further grouping needed for a simple trend line
        "x_axis_title": "Hour of Day",
        "y_axis_title": "Clicks",
        "show_legend": True,
    }

    payload = {
        "slice_name": slice_name,
        "viz_type": params["viz_type"],
        "datasource_id": datasource_id,
        "datasource_type": "table",
        "params": json.dumps(params),
    }

    print(f"Creating chart for {slice_name}...")
    try:
        resp = client._request("POST", "/api/v1/chart/", json=payload)
        chart_id = resp.json()["id"]
        print(f"Successfully created chart '{slice_name}' with ID: {chart_id}")
        return chart_id
    except Exception as e:
        print(f"!!! Failed to create chart '{slice_name}': {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    create_hourly_trend_chart()
