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
    """Main function to configure the new v_ga_event_trends dataset."""
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

    # 2. Clean the columns, removing read-only fields
    cleaned_columns = []
    for col in dataset_data.get("columns", []):
        cleaned_col = {
            "column_name": col["column_name"],
            "verbose_name": col.get("verbose_name"),
            "description": col.get("description"),
            "is_dttm": col.get("is_dttm", False),
            "is_active": col.get("is_active", True),
            "filterable": col.get("filterable", True),
            "groupby": col.get("groupby", True),
            "python_date_format": col.get("python_date_format"),
            "type": col.get("type")
        }
        # Set is_dttm for our target column
        if cleaned_col["column_name"] == "event_date":
            cleaned_col["is_dttm"] = True
        cleaned_columns.append(cleaned_col)

    # 3. Define metrics using the "reset and recreate" strategy
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

    # 4. Construct the final payload
    update_payload = {
        "main_dttm_col": "event_date",
        "columns": cleaned_columns,
        "metrics": new_metrics
    }

    # 5. Update the dataset
    update_command = [
        python_executable,
        api_client_path,
        "update_dataset",
        "--dataset_id", str(dataset_id),
        "--payload", json.dumps(update_payload)
    ]
    print("\n--- Updating dataset with new settings ---")
    run_command(update_command)

if __name__ == "__main__":
    main()