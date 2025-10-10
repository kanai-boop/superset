import sys
import os
sys.path.append(os.getcwd())

import json
import uuid
from scripts.superset_tools.api_client import SupersetClient

def add_chart_to_dashboard():
    """
    Adds a chart to a specified dashboard.
    """
    client = SupersetClient()
    client.login()

    dashboard_id = 12
    chart_id = 306 # The new WoW Performance Snapshot chart
    chart_title = "WoW Performance Snapshot"

    print(f"Adding chart {chart_id} ('{chart_title}') to dashboard {dashboard_id}...")
    try:
        dashboard = client.get_dashboard(dashboard_id)
        position_data = json.loads(dashboard["position_json"])

        # Create new chart component
        new_chart_uuid = f"CHART-{uuid.uuid4().hex}"
        new_chart_component = {
            "id": new_chart_uuid,
            "type": "CHART",
            "children": [],
            "meta": {
                "width": 12, # Full width
                "height": 50,
                "chartId": chart_id,
                "sliceName": chart_title,
                "uuid": str(uuid.uuid4())
            }
        }

        # Create a new row for the chart
        new_row_uuid = f"ROW-{uuid.uuid4().hex}"
        new_row_component = {
            "id": new_row_uuid,
            "type": "ROW",
            "children": [new_chart_uuid],
            "meta": {"background": "BACKGROUND_TRANSPARENT"}
        }

        # Add the new components to the layout
        position_data[new_chart_uuid] = new_chart_component
        position_data[new_row_uuid] = new_row_component

        # Add the new row to the grid
        grid_id = "GRID_ID"
        position_data[grid_id]["children"].append(new_row_uuid)
        
        new_chart_component["parents"] = ["ROOT_ID", grid_id, new_row_uuid]
        new_row_component["parents"] = ["ROOT_ID", grid_id]

        # Prepare the update payload
        update_payload = {
            "dashboard_title": dashboard["dashboard_title"],
            "css": dashboard["css"],
            "json_metadata": dashboard["json_metadata"],
            "owners": [owner["id"] for owner in dashboard.get("owners", [])],
            "position_json": json.dumps(position_data),
            "published": dashboard["published"],
            "slug": dashboard.get("slug"),
        }

        client.update_dashboard(dashboard_id, update_payload)
        print("Successfully added chart to dashboard.")

    except Exception as e:
        print(f"!!! Failed to add chart to dashboard: {e}")

if __name__ == "__main__":
    add_chart_to_dashboard()