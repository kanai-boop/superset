import json
from superset_tools.api_client import SupersetClient

def add_engagement_rate_metric():
    """
    Adds the 'Engagement Rate' metric to the v_ga_sessions dataset (ID 34)
    using a reset-and-recreate strategy.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 34
    print(f"Fetching existing metrics for dataset {dataset_id}...")

    try:
        # Fetch the full dataset definition to get the existing metrics
        dataset_info = client.get_dataset(dataset_id, q={'columns': ['metrics']})
        existing_metrics = dataset_info['result']['metrics']
        print(f"Found {len(existing_metrics)} existing metrics.")

        # Define the new metric
        new_metric = {
            "metric_name": "Engagement Rate",
            "verbose_name": "Engagement Rate",
            "metric_type": "expression",
            "expression": "SUM(CASE WHEN is_engaged_session THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT unique_session_id), 0)",
            "d3format": ".2%",
            "description": "(Engaged Sessions / Sessions). An engaged session is a session that lasts longer than 10 seconds, has a conversion event, or has at least 2 pageviews or screenviews."
        }

        # Check if the metric already exists by name
        metric_exists = any(m['metric_name'] == new_metric['metric_name'] for m in existing_metrics)

        # Remove fields that should not be in the PUT payload for recreation
        for metric in existing_metrics:
            metric.pop('id', None)
            metric.pop('uuid', None)
            metric.pop('changed_on', None)
            metric.pop('created_on', None)
        
        final_metrics_list = existing_metrics
        if not metric_exists:
            final_metrics_list.append(new_metric)
            print(f"Metric ''{new_metric['metric_name']}'' will be added.")
        else:
            print(f"Metric ''{new_metric['metric_name']}'' already exists. Recreating all metrics including it.")

        # --- Reset and Recreate Strategy ---
        # 1. Reset: Send an empty list to delete all metrics
        print("Resetting metrics...")
        client.update_dataset(dataset_id, {"metrics": []})
        print("Metrics reset successfully.")

        # 2. Recreate: Send the full list of metrics back
        print(f"Recreating {len(final_metrics_list)} metrics...")
        payload = {"metrics": final_metrics_list}
        client.update_dataset(dataset_id, payload)
        print("Successfully recreated all metrics.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    add_engagement_rate_metric()