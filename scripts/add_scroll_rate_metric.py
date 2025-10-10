

import json
import subprocess
import os

def run_command(command):
    """Runs a shell command and prints its output."""
    print(f"Executing: {' '.join(command)}")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=project_root
    )
    if process.stdout:
        print("STDOUT:", process.stdout)
    if process.stderr:
        print("STDERR:", process.stderr)
    return process

def main():
    """Main function to add a Scroll Rate metric to Dataset 36."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_executable = os.path.join(project_root, "venv", "bin", "python")
    api_client_path = os.path.join(project_root, "scripts", "superset_tools", "api_client.py")
    dataset_id = 36

    # Step 1: Get the current dataset definition to retrieve existing metrics
    get_command = [
        python_executable,
        api_client_path,
        "get_dataset",
        "--dataset_id", str(dataset_id)
    ]
    result = run_command(get_command)
    if result.returncode != 0:
        print("Failed to get dataset details. Aborting.")
        return

    dataset_data = json.loads(result.stdout)
    existing_metrics = dataset_data.get("result", {}).get("metrics", [])

    # Remove ids from existing metrics for re-creation
    for metric in existing_metrics:
        metric.pop('id', None)
        metric.pop('uuid', None)
        metric.pop('changed_on', None)
        metric.pop('created_on', None)

    # Step 2: Define the new metric
    new_metric = {
        "metric_name": "Scroll Rate",
        "verbose_name": "Scroll Rate",
        "metric_type": "expression",
        "expression": "SUM(CASE WHEN event_name = 'scroll' THEN event_count ELSE 0 END) / NULLIF(SUM(CASE WHEN event_name = 'page_view' THEN event_count ELSE 0 END), 0)",
        "d3format": ".2%",
        "description": "Percentage of page views that involved a scroll action."
    }
    
    all_metrics = existing_metrics + [new_metric]

    # Step 3: Use the "reset and recreate" strategy to update the dataset
    # Stage 1: Delete all metrics
    update_payload_delete = {"metrics": []}
    delete_command = [
        python_executable,
        api_client_path,
        "update_dataset",
        "--dataset_id", str(dataset_id),
        "--payload", json.dumps(update_payload_delete)
    ]
    print("\n--- Stage 1: Deleting all metrics ---")
    run_command(delete_command)

    # Stage 2: Re-create all metrics including the new one
    update_payload_recreate = {"metrics": all_metrics}
    recreate_command = [
        python_executable,
        api_client_path,
        "update_dataset",
        "--dataset_id", str(dataset_id),
        "--payload", json.dumps(update_payload_recreate)
    ]
    print("\n--- Stage 2: Re-creating all metrics with the new one ---")
    run_command(recreate_command)

if __name__ == "__main__":
    main()

