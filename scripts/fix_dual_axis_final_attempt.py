
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def fix_dual_axis_final_attempt(chart_id: int):
    """
    Attempts to fix a mixed time-series chart by explicitly setting all known
    parameters required for dual-axis display.
    """
    client = SupersetClient()
    client.login()

    print(f"Fetching chart {chart_id} to get base params...")
    chart_data = client.get_chart(chart_id)
    base_params = json.loads(chart_data.get("params", "{}"))

    print("Constructing a full payload for dual-axis display...")

    # Start with a clean slate for critical params, but keep others
    final_params = base_params

    # --- Query and Metric assignment ---
    final_params['metrics'] = ['cost']
    final_params['metrics_b'] = ['roas']
    if 'secondary_metrics' in final_params:
        del final_params['secondary_metrics']

    # --- Dual Axis Enablement ---
    final_params['use_y_axis_2'] = True

    # --- Chart Type Assignment ---
    # Explicitly define the chart type for both queries
    final_params['chart_type'] = 'line'
    final_params['chart_type_b'] = 'line'

    # --- Axis Formatting ---
    final_params['y_axis_format'] = '~s'  # SI format for cost
    final_params['y_axis_2_format'] = '.2%' # Percentage format for roas

    payload = {"params": json.dumps(final_params)}

    print("Updating chart with final attempt...")
    client.update_chart(chart_id, payload)

    print(f"Chart {chart_id} has been updated. Please check the UI carefully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.fix_dual_axis_final_attempt <chart_id>")
        sys.exit(1)

    try:
        chart_id_arg = int(sys.argv[1])
        fix_dual_axis_final_attempt(chart_id_arg)
    except ValueError:
        print("Error: Chart ID must be an integer.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

