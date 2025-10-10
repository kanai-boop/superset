
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def create_bignumber_charts():
    """
    Creates Big Number charts for CPA, CPC, CVR, and CPM.
    """
    client = SupersetClient()
    client.login()

    datasource_id = 31
    datasource_type = "table"

    chart_configs = [
        {
            "slice_name": "CPA",
            "metric": "cpa",
            "y_axis_format": ",.0f",
            "currency": {"symbol": "JPY", "symbolPosition": "prefix"},
        },
        {
            "slice_name": "CPC",
            "metric": "cpc",
            "y_axis_format": ",.0f",
            "currency": {"symbol": "JPY", "symbolPosition": "prefix"},
        },
        {
            "slice_name": "CVR",
            "metric": "cvr",
            "y_axis_format": ".2%",
        },
        {
            "slice_name": "CPM",
            "metric": "cpm",
            "y_axis_format": ",.0f",
            "currency": {"symbol": "JPY", "symbolPosition": "prefix"},
        },
    ]

    created_chart_ids = []
    for config in chart_configs:
        slice_name = config["slice_name"]
        metric = config["metric"]
        y_axis_format = config["y_axis_format"]
        currency = config.get("currency")

        params = {
            "metric": metric,
            "y_axis_format": y_axis_format,
            "compare_lag": 1,
            "comparison_type": "percentage",
            "subheader_font_size": 0.15,
            "show_delta": True,
            "show_percent": True,
        }
        if currency:
            params["currency_format"] = currency # This might be the correct key for BigNumber currency

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
            created_chart_ids.append(chart_id)
            print(f"Successfully created chart '{slice_name}' with ID: {chart_id}")
        except Exception as e:
            print(f"!!! Failed to create chart '{slice_name}': {e}", file=sys.stderr)

    print("\nAll Big Number charts created. IDs:", created_chart_ids)

if __name__ == "__main__":
    create_bignumber_charts()
