
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def create_empty_ga_dashboard():
    """
    Creates a new, empty GA Dashboard.
    """
    client = SupersetClient()
    client.login()

    dashboard_title = "GA Dashboard"

    print(f"Creating new empty dashboard '{dashboard_title}'...")
    try:
        create_payload = {
            "dashboard_title": dashboard_title,
            "owners": [1], # Assuming admin is owner
            "published": True,
            "position_json": json.dumps({
                "DASHBOARD_VERSION_KEY": "v2",
                "GRID_ID": {"children": [], "id": "GRID_ID", "type": "GRID"},
                "HEADER_ID": {"id": "HEADER_ID", "type": "HEADER", "meta": {"text": dashboard_title}},
                "ROOT_ID": {"children": ["GRID_ID"], "id": "ROOT_ID", "type": "ROOT"},
            }),
            "json_metadata": json.dumps({"chart_configuration": {}}),
        }
        resp = client._request("POST", "/api/v1/dashboard/", json=create_payload)
        dashboard_id = resp.json()["id"]
        print(f"Successfully created empty dashboard '{dashboard_title}' with ID: {dashboard_id}")
        return dashboard_id
    except Exception as e:
        print(f"!!! Failed to create empty dashboard '{dashboard_title}': {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    create_empty_ga_dashboard()
