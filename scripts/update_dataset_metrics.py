import json
import sys
import uuid
from scripts.superset_tools.api_client import SupersetClient

def update_dataset_metrics(dataset_id: int):
    """
    Updates a dataset by adding/modifying specified metrics.
    """
    client = SupersetClient()
    client.login()

    print(f"Fetching dataset {dataset_id}...")
    dataset = client.get_dataset(dataset_id)

    # Extract existing metrics and filter out read-only fields
    metrics = []
    for metric in dataset.get("metrics", []):
        filtered_metric = {
            k: v for k, v in metric.items() if k not in ["created_on", "changed_on"]
        }
        metrics.append(filtered_metric)

    # --- Modify existing CPA metric ---
    cpa_metric_found = False
    for metric in metrics:
        if metric.get("metric_name") == "cpa":
            metric["currency"] = {"symbol": "JPY", "symbolPosition": "prefix"}
            cpa_metric_found = True
            print("Modified existing 'cpa' metric with currency prefix.")
            break
    if not cpa_metric_found:
        print("Warning: 'cpa' metric not found in existing metrics. Skipping modification.")

    # --- Add new metrics if they don't exist ---
    new_metrics_to_add = [
        {
            "metric_name": "cpc",
            "verbose_name": "cpc",
            "expression": "SUM(metrics_cost_micros)/1e6 / NULLIF(SUM(metrics_clicks),0)",
            "d3format": ",.0f",
            "currency": {"symbol": "JPY", "symbolPosition": "prefix"},
            "metric_type": None, # Superset will infer or use 'expression'
        },
        {
            "metric_name": "cvr",
            "verbose_name": "cvr",
            "expression": "SUM(metrics_conversions) / NULLIF(SUM(metrics_clicks),0)",
            "d3format": ".2%",
            "metric_type": None,
        },
        {
            "metric_name": "cpm",
            "verbose_name": "cpm",
            "expression": "(SUM(metrics_cost_micros)/1e6) / NULLIF(SUM(metrics_impressions),0) * 1000",
            "d3format": ",.0f",
            "currency": {"symbol": "JPY", "symbolPosition": "prefix"},
            "metric_type": None,
        },
    ]

    for new_metric_data in new_metrics_to_add:
        metric_name = new_metric_data["metric_name"]
        if not any(m.get("metric_name") == metric_name for m in metrics):
            new_metric_data["uuid"] = str(uuid.uuid4())
            metrics.append(new_metric_data)
            print(f"Added new metric: '{metric_name}'.")
        else:
            print(f"Metric '{metric_name}' already exists. Skipping addition.")

    # Construct the payload for update_dataset with only allowed fields
    update_payload = {
        "database_id": dataset["database"]["id"],
        "owners": [owner["id"] for owner in dataset["owners"]],
        "schema": dataset.get("schema"),
        "table_name": dataset.get("table_name"),
        "main_dttm_col": dataset.get("main_dttm_col"),
        "metrics": metrics, # Send the updated metrics list
    }

    print(f"Updating dataset {dataset_id} with new metrics...")
    client.update_dataset(dataset_id, update_payload)
    print(f"Successfully updated dataset {dataset_id}.")

    print(f"Refreshing dataset {dataset_id} metadata...")
    client.refresh_dataset(dataset_id)
    print(f"Successfully refreshed dataset {dataset_id}.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.update_dataset_metrics <dataset_id>")
        sys.exit(1)

    try:
        dataset_id_arg = int(sys.argv[1])
        update_dataset_metrics(dataset_id_arg)
    except ValueError:
        print("Error: Dataset ID must be an integer.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)