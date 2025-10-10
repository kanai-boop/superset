

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
    """Adds a calculated column 'event_date_casted' to dataset 39."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_executable = os.path.join(project_root, "venv", "bin", "python")
    api_client_path = os.path.join(project_root, "scripts", "superset_tools", "api_client.py")
    dataset_id = 39

    # Define ONLY the new calculated column.
    # The API should add this to the existing columns.
    new_calculated_column = {
        "column_name": "event_date_casted",
        "verbose_name": "Event Date (Casted)",
        "is_dttm": True,
        "type": "DATE",
        "expression": "CAST(event_date AS DATE)",
        "is_active": True,
        "filterable": True,
        "groupby": True,
    }

    # The payload contains the columns list with only the new column.
    # The API should append it.
    update_payload = {
        "columns": [new_calculated_column],
    }

    # Update the dataset
    update_command = [
        python_executable,
        api_client_path,
        "update_dataset",
        "--dataset_id", str(dataset_id),
        "--payload", json.dumps(update_payload)
    ]
    print("\n--- Adding new calculated column to dataset ---")
    run_command(update_command)

if __name__ == "__main__":
    main()
