
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def create_revenue_bignumber_chart():
    """
    Creates a Big Number chart for Revenue.
    """
    client = SupersetClient()
    client.login()

    datasource_id = 31
    datasource_type = "table"

    slice_name = "Revenue"
    metric = "revenue"
    y_axis_format = "$,.2f" # From dataset definition

    params = {
        "metric": metric,
        "y_axis_format": y_axis_format,
        "compare_lag": 1,
        "comparison_type": "percentage",
        "subheader_font_size": 0.15,
        "show_delta": True,
        "show_percent": True,
    }

    payload = {
        "slice_name": slice_name,
        "viz_type": "big_number",
        "datasource_id": datasource_id,
        "datasource_type": datasource_type,
        "params": json.dumps(params),
    }

    print(f"Creating Big Number chart for {slice_name}...")
    try:
        resp = client._request("POST", "/api/v1/chart/", json=payload)
        chart_id = resp.json()["id"]
        print(f"Successfully created chart '{slice_name}' with ID: {chart_id}")
    except Exception as e:
        print(f"!!! Failed to create chart '{slice_name}': {e}", file=sys.stderr)

if __name__ == "__main__":
    create_revenue_bignumber_chart()
