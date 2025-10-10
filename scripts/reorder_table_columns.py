
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def reorder_table_columns(chart_id: int):
    """
    Reorders columns in a table chart based on a specified list.
    """
    client = SupersetClient()
    client.login()

    print(f"Fetching chart {chart_id}...")
    chart_data = client.get_chart(chart_id)
    params = json.loads(chart_data.get("params", "{}"))

    print("Setting explicit column order...")

    # Desired column order
    desired_columns = [
        "campaign_base_campaign",
        "cost",
        "clicks",
        "impressions",
        "ctr",
        "conversions",
        "cpa",
        "roas"
    ]

    # Overwrite the 'columns' parameter with the desired order
    # This parameter explicitly controls the display order in table charts.
    params['columns'] = desired_columns

    payload = {"params": json.dumps(params)}

    print("Updating chart...")
    client.update_chart(chart_id, payload)

    print(f"Chart {chart_id} columns reordered successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.reorder_table_columns <chart_id>")
        sys.exit(1)

    try:
        chart_id_arg = int(sys.argv[1])
        reorder_table_columns(chart_id_arg)
    except ValueError:
        print("Error: Chart ID must be an integer.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

