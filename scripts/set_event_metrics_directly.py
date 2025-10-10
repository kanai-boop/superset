
import json
from superset_tools.api_client import SupersetClient

def set_event_dataset_metrics(dataset_id: int):
    """
    Sets a predefined list of event-related metrics to a given dataset,
    overwriting any existing metrics.
    """
    client = SupersetClient()
    client.login()

    # Define the complete list of metrics the dataset should have.
    final_metrics_payload = {
        "metrics": [
            {
                "metric_name": "count",
                "verbose_name": "COUNT(*)",
                "expression": "COUNT(*)",
                "metric_type": "count",
                "d3format": ",d",
            },
            {
                "metric_name": "Event Count",
                "verbose_name": "Event Count",
                "expression": "SUM(event_count)",
                "metric_type": "sum",
                "d3format": ",d",
            },
            {
                "metric_name": "Users",
                "verbose_name": "Users",
                "expression": "SUM(users)",
                "metric_type": "sum",
                "d3format": ",d",
            },
            {
                "metric_name": "Conversions",
                "verbose_name": "Conversions",
                "expression": "SUM(conversions)",
                "metric_type": "sum",
                "d3format": ",d",
            },
        ]
    }

    print(f"Attempting to overwrite metrics for dataset {dataset_id}...")

    try:
        client.update_dataset(dataset_id, final_metrics_payload)
        print(f"Successfully set {len(final_metrics_payload['metrics'])} metrics on dataset {dataset_id}.")
    except Exception as e:
        print(f"Error updating dataset {dataset_id}: {e}")


if __name__ == "__main__":
    DATASET_ID = 36
    set_event_dataset_metrics(DATASET_ID)
