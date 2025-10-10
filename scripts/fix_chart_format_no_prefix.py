
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def fix_chart_column_format_no_prefix(chart_id: int):
    """
    Fetches a chart, adds column formatting (without prefix), and updates it.
    """
    client = SupersetClient()
    client.login()

    print(f"Fetching chart {chart_id}...")
    chart_data = client.get_chart(chart_id)
    
    params_str = chart_data.get("params")
    if not params_str:
        print("Error: Chart has no 'params' field.")
        return

    params = json.loads(params_str)

    print("Applying column config without prefix...")
    # Note: The 'prefix' key is removed to isolate the problem.
    column_config = {
        "cost": {"d3_format": ",.0f"},
        "cpa": {"d3_format": ",.0f"},
        "ctr": {"d3_format": ".2%"},
        "roas": {"d3_format": ".2%"}
    }
    params['column_config'] = column_config

    payload = {"params": json.dumps(params)}

    print("Updating chart...")
    client.update_chart(chart_id, payload)

    print(f"Chart {chart_id} has been updated successfully with no prefix.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.fix_chart_format_no_prefix <chart_id>")
        sys.exit(1)

    try:
        chart_id_arg = int(sys.argv[1])
        fix_chart_column_format_no_prefix(chart_id_arg)
    except ValueError:
        print("Error: Chart ID must be an integer.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

