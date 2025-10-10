
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def create_ga_trend_chart():
    """
    Creates a Daily Sessions & Users Trend line chart using dataset 33.
    """
    client = SupersetClient()
    client.login()

    datasource_id = 33
    slice_name = "GA: Daily Sessions & Users Trend"

    params = {
        "datasource": f"{datasource_id}__table",
        "viz_type": "echarts_timeseries_line",
        "x_axis": "event_date_parsed",
        "metrics": ["sessions", "users"],
        "time_grain_sqla": "P1D", # Aggregate by day
        "adhoc_filters": [
            {
                "clause": "WHERE",
                "subject": "event_date_parsed",
                "operator": "TEMPORAL_RANGE",
                "comparator": "Last 90 days", # Default time range
                "expressionType": "SIMPLE"
            }
        ],
        "row_limit": 10000,
        "groupby": [],
        "x_axis_title": "Date",
        "y_axis_title": "Count",
        "show_legend": True,
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
    create_ga_trend_chart()
