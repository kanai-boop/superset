
import json
import subprocess
import os

def run_command(command):
    """Runs a shell command and returns its stdout."""
    print(f"Executing: {' '.join(command)}")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=project_root
    )
    if process.stderr:
        print("STDERR:", process.stderr)
    if process.stdout:
        print("STDOUT:", process.stdout)
    return process.stdout

def main():
    """Adds back the time comparison parameters to all 24 KPI charts."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_executable = os.path.join(project_root, "venv", "bin", "python")
    api_client_path = os.path.join(project_root, "scripts", "superset_tools", "api_client.py")

    chart_ids = [
        # Current Month
        348, 351, 354, 357, 360, 363, 366, 369,
        # Last Month
        349, 352, 355, 358, 361, 364, 367, 370,
        # 2 Months Ago
        350, 353, 356, 359, 362, 365, 368, 371,
    ]

    for chart_id in chart_ids:
        print(f"\n--- Adding time comparison to Chart ID: {chart_id} ---")
        
        # 1. Get current chart details
        get_command = [python_executable, api_client_path, "get_chart", "--chart_id", str(chart_id)]
        chart_details_str = run_command(get_command)
        if not chart_details_str:
            print(f"Error: Failed to get details for chart {chart_id}. Skipping.")
            continue
            
        chart_details = json.loads(chart_details_str)
        params = json.loads(chart_details.get("result", {}).get("params"))

        # 2. Add time comparison params
        params["compare_lag"] = 1
        params["comparison_type"] = "percentage"
        params["show_delta"] = True
        print(f"Added time comparison parameters to chart {chart_id}.")

        # 3. Update the chart
        update_payload = {"params": json.dumps(params)}
        update_command = [
            python_executable,
            api_client_path,
            "update_chart",
            "--chart_id", str(chart_id),
            "--payload", json.dumps(update_payload)
        ]
        run_command(update_command)
        print(f"--- Finished Processing Chart ID: {chart_id} ---")

if __name__ == "__main__":
    main()
