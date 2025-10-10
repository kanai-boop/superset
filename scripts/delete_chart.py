
import sys
import os
sys.path.append(os.getcwd())

from scripts.superset_tools.api_client import SupersetClient

def delete_chart():
    """
    Deletes a specified chart.
    """
    client = SupersetClient()
    client.login()

    chart_id_to_delete = 304

    print(f"Deleting chart {chart_id_to_delete}...")
    try:
        client.delete_chart(chart_id_to_delete)
        print(f"Successfully deleted chart {chart_id_to_delete}.")
    except Exception as e:
        print(f"!!! Failed to delete chart: {e}")

if __name__ == "__main__":
    delete_chart()
