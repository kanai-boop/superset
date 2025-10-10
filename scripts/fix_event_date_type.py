

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
    """Main function to fix the column type of event_date in dataset 39."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_executable = os.path.join(project_root, "venv", "bin", "python")
    api_client_path = os.path.join(project_root, "scripts", "superset_tools", "api_client.py")
    dataset_id = 39

    # 1. Get the current dataset definition to get column IDs
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

    # 2. Construct the payload to update the column type
    cleaned_columns = []
    for col in dataset_data.get("columns", []):
        # For updates, we need to keep the ID and only send changed fields if possible
        # but the API expects the full list. We must also strip read-only fields.
        cleaned_col = {
            "id": col["id"],
            "column_name": col["column_name"],
            "is_dttm": col.get("is_dttm", False),
            "type": col.get("type")
        }
        if cleaned_col["column_name"] == "event_date":
            cleaned_col["is_dttm"] = True
            cleaned_col["type"] = "DATE" # Explicitly set the type
        cleaned_columns.append(cleaned_col)

    update_payload = {
        "columns": cleaned_columns,
    }

    # 3. Update the dataset
    update_command = [
        python_executable,
        api_client_path,
        "update_dataset",
        "--dataset_id", str(dataset_id),
        "--payload", json.dumps(update_payload)
    ]
    print("\n--- Updating dataset with corrected column type ---")
    run_command(update_command)

if __name__ == "__main__":
    main()

