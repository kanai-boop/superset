
import json
from superset_tools.api_client import SupersetClient

def set_ga_dataset_metrics(dataset_id: int):
    """
    Sets a predefined list of GA4 metrics to a given dataset,
    overwriting any existing metrics.
    """
    client = SupersetClient()
    client.login()

    # Define the complete list of metrics the dataset should have.
    # This includes a basic count(*) and all our desired GA4 metrics.
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
                "metric_name": "Sessions",
                "verbose_name": "Sessions",
                "expression": "COUNT(DISTINCT unique_session_id)",
                "metric_type": "count_distinct",
                "d3format": ",d",
            },
            {
                "metric_name": "Users",
                "verbose_name": "Users",
                "expression": "COUNT(DISTINCT user_pseudo_id)",
                "metric_type": "count_distinct",
                "d3format": ",d",
            },
            {
                "metric_name": "Revenue",
                "verbose_name": "Revenue",
                "expression": "SUM(revenue)",
                "metric_type": "sum",
                "d3format": "¥,.0f",
            },
            {
                "metric_name": "Conversions",
                "verbose_name": "Conversions",
                "expression": "SUM(conversions)",
                "metric_type": "sum",
                "d3format": ",d",
            },
            {
                "metric_name": "Conversion Rate",
                "verbose_name": "Conversion Rate",
                "expression": "SUM(conversions) / NULLIF(COUNT(DISTINCT unique_session_id), 0)",
                "metric_type": "expression",
                "d3format": ".2%",
            },
            {
                "metric_name": "AOV",
                "verbose_name": "AOV (Average Order Value)",
                "expression": "SUM(revenue) / NULLIF(SUM(conversions), 0)",
                "metric_type": "expression",
                "d3format": "¥,.0f",
            },
            {
                "metric_name": "Avg Engagement Time (sec)",
                "verbose_name": "Avg Engagement Time (sec)",
                "expression": "AVG(total_engagement_time_msec) / 1000",
                "metric_type": "expression",
                "d3format": ",.1fS",
            },
            {
                "metric_name": "Bounce Rate (Proxy)",
                "verbose_name": "Bounce Rate (Proxy)",
                "expression": "1 - (SUM(CASE WHEN is_engaged_session THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT unique_session_id), 0))",
                "metric_type": "expression",
                "d3format": ".2%",
            },
            {
                "metric_name": "Engaged Sessions",
                "verbose_name": "Engaged Sessions",
                "expression": "SUM(CASE WHEN is_engaged_session THEN 1 ELSE 0 END)",
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
    DATASET_ID = 34
    set_ga_dataset_metrics(DATASET_ID)
