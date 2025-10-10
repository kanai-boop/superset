
import json
from superset_tools.api_client import SupersetClient

def setup_ga_dataset(dataset_id: int):
    """
    Adds a predefined set of GA4 metrics to a given dataset.
    """
    client = SupersetClient()
    client.login()

    # Refresh dataset to avoid cache issues
    try:
        print("Refreshing dataset to clear cache...")
        client.refresh_dataset(dataset_id)
        print("Dataset refreshed.")
    except Exception as e:
        print(f"Warning: Could not refresh dataset {dataset_id}. Proceeding anyway. Error: {e}")

    # Get existing dataset definition
    try:
        dataset_data = client.get_dataset(dataset_id)
        if not dataset_data:
            print(f"Error: Dataset with ID {dataset_id} not found.")
            return
    except Exception as e:
        print(f"Error fetching dataset {dataset_id}: {e}")
        return

    def clean_metric(metric: dict) -> dict:
        """Removes read-only fields from a metric dictionary."""
        allowed_keys = {
            "metric_name", "verbose_name", "expression", "metric_type",
            "d3format", "description", "extra", "warning_text"
        }
        # Ensure currency is only included if it's not None, though we remove it later
        cleaned = {k: v for k, v in metric.items() if k in allowed_keys and v is not None}
        return cleaned

    existing_metrics = dataset_data.get("metrics", [])
    cleaned_existing_metrics = [clean_metric(m) for m in existing_metrics]
    existing_metric_names = {m.get("metric_name") for m in cleaned_existing_metrics}
    
    print(f"Found {len(cleaned_existing_metrics)} existing metrics.")

    # Define new GA4 metrics (without the 'currency' key)
    new_metrics = [
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

    # Filter out metrics that already exist
    metrics_to_add = [m for m in new_metrics if m["metric_name"] not in existing_metric_names]
    if not metrics_to_add:
        print("All metrics already exist in the dataset. No changes made.")
        return

    print(f"Adding {len(metrics_to_add)} new metrics...")
    all_metrics = cleaned_existing_metrics + metrics_to_add

    payload = {"metrics": all_metrics}

    try:
        client.update_dataset(dataset_id, payload)
        print(f"Successfully updated dataset {dataset_id} with new metrics.")
    except Exception as e:
        print(f"Error updating dataset {dataset_id}: {e}")


if __name__ == "__main__":
    DATASET_ID = 34
    setup_ga_dataset(DATASET_ID)
