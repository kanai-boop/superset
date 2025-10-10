
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def create_efficiency_trends_charts():
    """
    Creates dual-axis mixed_timeseries charts for Efficiency Trends.
    """
    client = SupersetClient()
    client.login()

    datasource_id = 31
    datasource_type = "table"

    chart_configs = [
        {
            "slice_name": "Efficiency Trends (CPA & CVR)",
            "metrics_left": "cpa",
            "metrics_right": "cvr",
            "y_axis_format_left": "~s",
            "y_axis_format_right": ".2%",
        },
        {
            "slice_name": "Efficiency Trends (CPC & CTR)",
            "metrics_left": "cpc",
            "metrics_right": "ctr",
            "y_axis_format_left": "~s",
            "y_axis_format_right": ".2%",
        },
    ]

    created_chart_ids = []
    for config in chart_configs:
        slice_name = config["slice_name"]
        metric_left = config["metrics_left"]
        metric_right = config["metrics_right"]
        y_axis_format_left = config["y_axis_format_left"]
        y_axis_format_right = config["y_axis_format_right"]

        params = {
            "datasource": f"{datasource_id}__table",
            "viz_type": "mixed_timeseries",
            "x_axis": "segments_date", # Assuming segments_date is the time column
            "time_grain_sqla": "P1D", # Assuming daily granularity
            "metrics": [metric_left],
            "metrics_b": [metric_right],
            "yAxisIndex": 0,
            "yAxisIndexB": 1,
            "seriesType": "line",
            "seriesTypeB": "line",
            "y_axis_format": y_axis_format_left,
            "y_axis_format_secondary": y_axis_format_right,
            "use_y_axis_2": True,
            # Add other common mixed_timeseries params for completeness
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "subject": "segments_date",
                    "operator": "TEMPORAL_RANGE",
                    "comparator": "No filter",
                    "expressionType": "SIMPLE",
                }
            ],
            "order_desc": True,
            "row_limit": 10000,
            "truncate_metric": True,
            "comparison_type": "values",
            "annotation_layers": [],
            "x_axis_title_margin": 15,
            "y_axis_title_margin": 30,
            "y_axis_title_position": "Left",
            "color_scheme": "supersetColors",
            "time_shift_color": True,
            "stack": False,
            "area": False,
            "show_value": False,
            "only_total": True,
            "opacity": 0.2,
            "markerSize": 6,
            "sort_series_type": "sum",
            "sort_series_ascending": False,
            "markerEnabledB": False,
            "markerSizeB": 7,
            "sort_series_typeB": "sum",
            "zoomable": False,
            "minorTicks": False,
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
            "y_axis_bounds_secondary": [None, None],
            "logAxisSecondary": False,
            "extra_form_data": {},
            "dashboards": [],
        }

        payload = {
            "slice_name": slice_name,
            "viz_type": "mixed_timeseries",
            "datasource_id": datasource_id,
            "datasource_type": datasource_type,
            "params": json.dumps(params),
        }

        print(f"Creating Efficiency Trends chart for {slice_name}...")
        try:
            resp = client._request("POST", "/api/v1/chart/", json=payload)
            chart_id = resp.json()["id"]
            created_chart_ids.append(chart_id)
            print(f"Successfully created chart '{slice_name}' with ID: {chart_id}")
        except Exception as e:
            print(f"!!! Failed to create chart '{slice_name}': {e}", file=sys.stderr)

    print("\nAll Efficiency Trends charts created. IDs:", created_chart_ids)

if __name__ == "__main__":
    create_efficiency_trends_charts()
