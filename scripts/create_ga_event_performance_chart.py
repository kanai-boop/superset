
import json
from superset_tools.api_client import SupersetClient

def create_event_performance_chart():
    """
    Creates the Event Performance chart for the GA Dashboard.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 36 # v_ga_event_performance dataset

    charts_to_create = [
        {
            "chart_name": "GA: Event Performance",
            "viz_type": "table",
            "params": {
                "groupby": ["event_name"],
                "metrics": ["Event Count", "Users", "Conversions"],
                "all_columns": ["event_name"],
                "row_limit": 25,
            }
        },
    ]

    print(f"Creating {len(charts_to_create)} chart for dataset {dataset_id}...")

    for chart_def in charts_to_create:
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
    create_event_performance_chart()
