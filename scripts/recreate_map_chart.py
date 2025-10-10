

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
    """Recreates the world map chart with the correct filters."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_executable = os.path.join(project_root, "venv", "bin", "python")
    api_client_path = os.path.join(project_root, "scripts", "superset_tools", "api_client.py")

    # Define the chart payload as a Python dictionary
    params = {
        "viz_type": "world_map",
        "entity": "geo_country",
        "country_fieldtype": "country_name",
        "metric": "Users",
        "color_scheme": "greens",
        "adhoc_filters": [
            {
                "expressionType": "SQL",
                "sqlExpression": "geo_country IS NOT NULL AND geo_country != ''",
                "clause": "WHERE"
            }
        ]
    }

    payload = {
        "slice_name": "GA: User Distribution by Country",
        "viz_type": "world_map",
        "datasource_id": 34,
        "datasource_type": "table",
        "params": json.dumps(params) # The API expects the params value to be a string
    }

    # Create the chart
    command = [
        python_executable,
        api_client_path,
        "create_chart",
        "--payload", json.dumps(payload)
    ]
    print("\n--- Re-creating the map chart with correct filters ---")
    run_command(command)

if __name__ == "__main__":
    main()

