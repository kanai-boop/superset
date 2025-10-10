

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
    """Main function to configure the new v_ga_event_trends dataset in stages."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_executable = os.path.join(project_root, "venv", "bin", "python")
    api_client_path = os.path.join(project_root, "scripts", "superset_tools", "api_client.py")
    dataset_id = 39

    # 1. Get the current dataset definition
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
    
    dataset_data = json.loads(result.stdout)["result"]

    # --- Stage 1: Update Columns and Main DTTM Column ---
    print("\n--- Stage 1: Updating columns and main_dttm_col ---")
    cleaned_columns = []
    for col in dataset_data.get("columns", []):
        # For updates, we need to keep the ID
        cleaned_col = {
            "id": col["id"],
            "column_name": col["column_name"],
            "is_dttm": col.get("is_dttm", False),
        }
        if cleaned_col["column_name"] == "event_date":
            cleaned_col["is_dttm"] = True
        cleaned_columns.append(cleaned_col)

    update_columns_payload = {
        "main_dttm_col": "event_date",
        "columns": cleaned_columns,
    }

    update_columns_command = [
        python_executable,
        api_client_path,
        "update_dataset",
        "--dataset_id", str(dataset_id),
        "--payload", json.dumps(update_columns_payload)
    ]
    run_command(update_columns_command)

    # --- Stage 2: Update Metrics using Reset & Recreate ---
    print("\n--- Stage 2: Resetting metrics ---")
    delete_metrics_payload = {"metrics": []}
    delete_metrics_command = [
        python_executable,
        api_client_path,
        "update_dataset",
        "--dataset_id", str(dataset_id),
        "--payload", json.dumps(delete_metrics_payload)
    ]
    run_command(delete_metrics_command)

    print("\n--- Stage 3: Re-creating metrics ---")
    new_metrics = [
        {
            "metric_name": "count",
            "expression": "COUNT(*)",
            "verbose_name": "COUNT(*)",
            "metric_type": "count"
        },
        {
            "metric_name": "Scroll Rate",
            "verbose_name": "Scroll Rate",
            "metric_type": "expression",
            "expression": "SUM(CASE WHEN event_name = 'scroll' THEN event_count ELSE 0 END) / NULLIF(SUM(CASE WHEN event_name = 'page_view' THEN event_count ELSE 0 END), 0)",
            "d3format": ".2%",
            "description": "Percentage of page views that involved a scroll action."
        }
    ]
    recreate_metrics_payload = {"metrics": new_metrics}
    recreate_metrics_command = [
        python_executable,
        api_client_path,
        "update_dataset",
        "--dataset_id", str(dataset_id),
        "--payload", json.dumps(recreate_metrics_payload)
    ]
    run_command(recreate_metrics_command)

if __name__ == "__main__":
    main()

