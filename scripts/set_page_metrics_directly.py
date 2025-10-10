
import json
from superset_tools.api_client import SupersetClient

def set_page_dataset_metrics(dataset_id: int):
    """
    Sets a predefined list of page-related metrics to a given dataset,
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
                "metric_name": "Page Views",
                "verbose_name": "Page Views",
                "expression": "SUM(page_views)",
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
                "metric_name": "Total Engagement Seconds",
                "verbose_name": "Total Engagement Seconds",
                "expression": "SUM(total_engagement_seconds)",
                "metric_type": "sum",
                "d3format": ",.0f",
            },
            {
                "metric_name": "Sessions",
                "verbose_name": "Sessions",
                "expression": "SUM(sessions)",
                "metric_type": "sum",
                "d3format": ",d",
            },
            {
                "metric_name": "Avg Engagement Time per View (sec)",
                "verbose_name": "Avg Engagement Time per View (sec)",
                "expression": "SUM(total_engagement_seconds) / NULLIF(SUM(page_views), 0)",
                "metric_type": "expression",
                "d3format": ",.1f",
            },
            {
                "metric_name": "Avg Engagement Time per User (sec)",
                "verbose_name": "Avg Engagement Time per User (sec)",
                "expression": "SUM(total_engagement_seconds) / NULLIF(SUM(users), 0)",
                "metric_type": "expression",
                "d3format": ",.1f",
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
    DATASET_ID = 35
    set_page_dataset_metrics(DATASET_ID)
