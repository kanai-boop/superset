
import json
from superset_tools.api_client import SupersetClient

def create_acquisition_charts():
    """
    Creates a series of charts for the Acquisition section of the GA Dashboard.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 34

    charts_to_create = [
        {
            "chart_name": "GA: Source/Medium Performance",
            "viz_type": "table",
            "params": {
                "groupby": ["source", "medium"],
                "metrics": ["Sessions", "Users", "Conversions", "Conversion Rate", "Revenue"],
                "all_columns": ["source", "medium"],
                "percent_metrics": ["Conversion Rate"], # Ensure this is formatted as a percentage
            }
        },
        {
            "chart_name": "GA: Top Campaigns",
            "viz_type": "table",
            "params": {
                "groupby": ["campaign"],
                "metrics": ["Sessions", "Users", "Conversions", "Revenue"],
                "all_columns": ["campaign"],
            }
        },
        {
            "chart_name": "GA: Device Category Breakdown",
            "viz_type": "bar",
            "params": {
                "groupby": ["device_category"],
                "metrics": ["Sessions"],
                "x_axis": "device_category",
                "y_axis": "Sessions",
                "rich_tooltip": True,
            }
        },
        {
            "chart_name": "GA: Top 10 Countries",
            "viz_type": "bar",
            "params": {
                "groupby": ["geo_country"],
                "metrics": ["Sessions"],
                "x_axis": "geo_country",
                "y_axis": "Sessions",
                "row_limit": 10,
                "rich_tooltip": True,
            }
        },
        {
            "chart_name": "GA: New vs Returning Users",
            "viz_type": "pie",
            "params": {
                "groupby": ["new_vs_returning"],
                "metric": "Users", # Pie chart uses 'metric' not 'metrics'
                "show_legend": True,
                "show_labels": True,
            }
        },
    ]

    print(f"Creating {len(charts_to_create)} acquisition charts for dataset {dataset_id}...")

    for chart_def in charts_to_create:
        # Common params for all charts
        chart_def["params"]["datasource"] = f"{dataset_id}__table"
        chart_def["params"]["time_range_endpoints"] = ["inclusive", "exclusive"]

        payload = {
            "slice_name": chart_def["chart_name"],
            "viz_type": chart_def["viz_type"],
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": json.dumps(chart_def["params"]),
        }

        try:
            result = client.create_chart(payload)
            new_chart_id = result.get("id")
            print(f"Successfully created chart ''{chart_def['chart_name']}'' with ID: {new_chart_id}")
        except Exception as e:
            print(f"Error creating chart ''{chart_def['chart_name']}'': {e}")

if __name__ == "__main__":
    create_acquisition_charts()
