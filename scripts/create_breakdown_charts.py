import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def create_breakdown_charts():
    """
    Creates stacked bar charts for Device and Network breakdowns.
    """
    client = SupersetClient()
    client.login()

    datasource_id = 31
    datasource_type = "table"

    common_metrics = ["clicks", "conversions", "cost", "impressions"]

    chart_configs = [
        {
            "slice_name": "Device Breakdown",
            "groupby_col": "segments_device", # Renamed to avoid confusion with params["groupby"]
            "viz_type": "echarts_timeseries_bar", # Corrected viz_type
            "stack": True,
            "metrics": common_metrics,
            "y_axis_format": "~s", # For general numbers
        },
        {
            "slice_name": "Network Breakdown",
            "groupby_col": "segments_ad_network_type", # Renamed
            "viz_type": "echarts_timeseries_bar", # Corrected viz_type
            "stack": True,
            "metrics": common_metrics,
            "y_axis_format": "~s",
        },
    ]

    created_chart_ids = []
    for config in chart_configs:
        slice_name = config["slice_name"]
        groupby_col = config["groupby_col"]
        metrics = config["metrics"]
        y_axis_format = config["y_axis_format"]
        stack = config["stack"]

        params = {
            "datasource": f"{datasource_id}__table",
            "viz_type": config["viz_type"],
            "x_axis": groupby_col, # Use x_axis for grouping
            "metrics": metrics,
            "groupby": [], # Set groupby to empty list
            "stack": stack,
            "y_axis_format": y_axis_format,
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "subject": "segments_date",
                    "operator": "TEMPORAL_RANGE",
                    "comparator": "No filter",
                    "expressionType": "SIMPLE",
                }
            ], # Keep adhoc_filters for segments_date
            "row_limit": 10000,
            "show_legend": True,
            "legendType": "scroll",
            "legendOrientation": "top",
            "x_axis_time_format": "smart_date",
            "xAxisLabelInterval": "auto",
            "rich_tooltip": True,
            "showTooltipTotal": True,
            "tooltipTimeFormat": "smart_date",
            "truncateXAxis": True,
            "y_axis_bounds": [None, None],
            "logAxis": False,
            "extra_form_data": {},
            "dashboards": [],
            "query_mode": "aggregate", # Keep query_mode
            # Removed time_grain_sqla and granularity_sqla
        }

        payload = {
            "slice_name": slice_name,
            "viz_type": config["viz_type"],
            "datasource_id": datasource_id,
            "datasource_type": datasource_type,
            "params": json.dumps(params),
        }

        print(f"Creating breakdown chart for {slice_name}...")
        try:
            resp = client._request("POST", "/api/v1/chart/", json=payload)
            chart_id = resp.json()["id"]
            created_chart_ids.append(chart_id)
            print(f"Successfully created chart '{slice_name}' with ID: {chart_id}")
        except Exception as e:
            print(f"!!! Failed to create chart '{slice_name}': {e}", file=sys.stderr)

    print("\nAll breakdown charts created. IDs:", created_chart_ids)

if __name__ == "__main__":
    create_breakdown_charts()