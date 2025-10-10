
import sys
import os
sys.path.append(os.getcwd())

from scripts.superset_tools.api_client import SupersetClient

def delete_dashboard():
    """
    Deletes a specified dashboard.
    """
    client = SupersetClient()
    client.login()

    dashboard_id_to_delete = 13

    print(f"Deleting dashboard {dashboard_id_to_delete}...")
    try:
        client.delete_dashboard(dashboard_id_to_delete)
        print(f"Successfully deleted dashboard {dashboard_id_to_delete}.")
    except Exception as e:
        print(f"!!! Failed to delete dashboard: {e}")

if __name__ == "__main__":
    delete_dashboard()
