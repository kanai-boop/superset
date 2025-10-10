
import json
from superset_tools.api_client import SupersetClient

def create_highlight_charts():
    """
    Creates a series of Big Number with Trendline charts for the GA Dashboard.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 34

    charts_to_create = [
        {"chart_name": "GA: Total Users", "metric": "Users"},
        {"chart_name": "GA: Total Sessions", "metric": "Sessions"},
        {"chart_name": "GA: Total Conversions", "metric": "Conversions"},
        {"chart_name": "GA: Total Revenue", "metric": "Revenue"},
        {"chart_name": "GA: Conversion Rate", "metric": "Conversion Rate"},
        {"chart_name": "GA: Avg Engagement Time", "metric": "Avg Engagement Time (sec)"},
    ]

    print(f"Creating {len(charts_to_create)} charts for dataset {dataset_id}...")

    for chart_def in charts_to_create:
        metric_name = chart_def["metric"]
        
        params = {
            "datasource": f"{dataset_id}__table",
            "viz_type": "big_number_with_trendline",
            "metric": {
                "label": metric_name
            },
            "time_range_endpoints": ["inclusive", "exclusive"],
            "time_grain_sqla": "P1D",
            "compare_lag": 1, # Compare to previous period
            "comparison_type": "percentage", # Show as percentage change
            "show_trend_line": True,
            "start_y_axis_at_zero": True,
            "show_delta": True,
            "show_percent": True,
            "subheader_font_size": 0.15, # Small
        }

        # Set the primary metric using its proper key if it's a saved metric
        # For ad-hoc metrics, this structure might differ slightly but this is robust
        params["metric"] = metric_name

        payload = {
            "slice_name": chart_def["chart_name"],
            "viz_type": "big_number_with_trendline",
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": json.dumps(params),
        }

        try:
            result = client.create_chart(payload)
            new_chart_id = result.get("id")
            print(f"Successfully created chart ''{chart_def['chart_name']}'' with ID: {new_chart_id}")
        except Exception as e:
            print(f"Error creating chart ''{chart_def['chart_name']}'': {e}")

if __name__ == "__main__":
    create_highlight_charts()
