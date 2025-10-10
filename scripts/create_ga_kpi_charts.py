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
    """Main function to create two Big Number charts for GA."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_executable = os.path.join(project_root, "venv", "bin", "python")
    api_client_path = os.path.join(project_root, "scripts", "superset_tools", "api_client.py")

    charts_to_create = [
        {
            "slice_name": "GA: Bounce Rate (Proxy)",
            "viz_type": "big_number",
            "datasource_id": 34,
            "datasource_type": "table",
            "params": {
                "metric": "Bounce Rate (Proxy)",
                "granularity_sqla": "session_start_timestamp",
                "time_grain_sqla": "P1D",
                "viz_type": "big_number",
                "show_trend_line": True,
                "start_y_axis_at_zero": False,
                "time_range_endpoints": ["inclusive", "exclusive"],
                "y_axis_format": ".2%",
                "time_range": "No filter",
                "compare_lag": "7",
                "compare_suffix": "WoW",
                "comparison_type": "percentage",
                "show_delta": True,
                "show_percent": True,
                "subheader_font_size": 0.15,
            }
        },
        {
            "slice_name": "GA: AOV",
            "viz_type": "big_number",
            "datasource_id": 34,
            "datasource_type": "table",
            "params": {
                "metric": "AOV",
                "granularity_sqla": "session_start_timestamp",
                "time_grain_sqla": "P1D",
                "viz_type": "big_number",
                "show_trend_line": True,
                "start_y_axis_at_zero": True,
                "time_range_endpoints": ["inclusive", "exclusive"],
                "y_axis_format": "¥,.0f",
                "time_range": "No filter",
                "compare_lag": "7",
                "compare_suffix": "WoW",
                "comparison_type": "percentage",
                "show_delta": True,
                "show_percent": True,
                "subheader_font_size": 0.15,
            }
        }
    ]

    for chart_payload in charts_to_create:
        # The api_client expects the params to be a string, so we dump it again.
        chart_payload["params"] = json.dumps(chart_payload["params"])
        
        command = [
            python_executable,
            api_client_path,
            "create_chart",
            "--payload", json.dumps(chart_payload)
        ]
        run_command(command)

if __name__ == "__main__":
    main()