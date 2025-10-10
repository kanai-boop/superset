import sys
import os
sys.path.append(os.getcwd())

import json
import uuid
from scripts.superset_tools.api_client import SupersetClient

def create_ga_dashboard():
    """
    Creates a new GA Dashboard and adds all GA charts to it.
    """
    client = SupersetClient()
    client.login()

    dashboard_title = "GA Dashboard"
    dashboard_id = 13 # We are updating an existing dashboard

    # 1. Get existing dashboard details to preserve other properties
    print(f"Fetching existing dashboard {dashboard_id}...")
    try:
        existing_dashboard = client.get_dashboard(dashboard_id)
        print(f"Found dashboard '{dashboard_title}' with ID: {dashboard_id}")
    except Exception as e:
        print(f"!!! Failed to fetch dashboard {dashboard_id}: {e}", file=sys.stderr)
        return

    # 2. Define the charts to add
    charts_to_add = [
        {"id": 308, "name": "GA: Total Sessions", "width": 6, "height": 30}, # Big Number
        {"id": 309, "name": "GA: Total Users", "width": 6, "height": 30}, # Big Number
        {"id": 307, "name": "GA: Daily Sessions & Users Trend", "width": 12, "height": 50}, # Line Chart
        {"id": 310, "name": "GA: Top 5 Traffic Sources", "width": 6, "height": 50}, # Pie Chart
        {"id": 311, "name": "GA: Top 10 Landing Pages", "width": 6, "height": 50}, # Table Chart
    ]

    # 3. Construct the position_json
    position_data = {
        "DASHBOARD_VERSION_KEY": "v2",
        "GRID_ID": {"children": [], "id": "GRID_ID", "type": "GRID"},
        "HEADER_ID": {"id": "HEADER_ID", "type": "HEADER", "meta": {"text": dashboard_title}},
        "ROOT_ID": {"children": ["GRID_ID"], "id": "ROOT_ID", "type": "ROOT"},
    }

    # Row 1: Big Numbers
    row1_id = f"ROW-{uuid.uuid4().hex}"
    position_data[row1_id] = {"children": [], "id": row1_id, "type": "ROW", "parents": ["ROOT_ID", "GRID_ID"], "meta": {"background": "BACKGROUND_TRANSPARENT"}}
    position_data["GRID_ID"]["children"].append(row1_id)

    # Row 2: Daily Trend
    row2_id = f"ROW-{uuid.uuid4().hex}"
    position_data[row2_id] = {"children": [], "id": row2_id, "type": "ROW", "parents": ["ROOT_ID", "GRID_ID"], "meta": {"background": "BACKGROUND_TRANSPARENT"}}
    position_data["GRID_ID"]["children"].append(row2_id)

    # Row 3: Traffic Source & Landing Pages
    row3_id = f"ROW-{uuid.uuid4().hex}"
    position_data[row3_id] = {"children": [], "id": row3_id, "type": "ROW", "parents": ["ROOT_ID", "GRID_ID"], "meta": {"background": "BACKGROUND_TRANSPARENT"}}
    position_data["GRID_ID"]["children"].append(row3_id)

    # Add charts to rows
    chart_uuids = {}
    for chart_info in charts_to_add:
        chart_uuid = f"CHART-{uuid.uuid4().hex}"
        chart_uuids[chart_info["id"]] = chart_uuid
        position_data[chart_uuid] = {
            "children": [],
            "id": chart_uuid,
            "meta": {
                "chartId": chart_info["id"],
                "height": chart_info["height"],
                "sliceName": chart_info["name"],
                "uuid": str(uuid.uuid4()),
                "width": chart_info["width"],
            },
            "parents": [], # Will be filled below
            "type": "CHART",
        }

    # Assign charts to rows and fill parents
    # Row 1: Big Numbers
    position_data[row1_id]["children"].append(chart_uuids[308])
    position_data[chart_uuids[308]]["parents"] = ["ROOT_ID", "GRID_ID", row1_id]
    position_data[row1_id]["children"].append(chart_uuids[309])
    position_data[chart_uuids[309]]["parents"] = ["ROOT_ID", "GRID_ID", row1_id]

    # Row 2: Daily Trend
    position_data[row2_id]["children"].append(chart_uuids[307])
    position_data[chart_uuids[307]]["parents"] = ["ROOT_ID", "GRID_ID", row2_id]

    # Row 3: Traffic Source & Landing Pages
    position_data[row3_id]["children"].append(chart_uuids[310])
    position_data[chart_uuids[310]]["parents"] = ["ROOT_ID", "GRID_ID", row3_id]
    position_data[row3_id]["children"].append(chart_uuids[311])
    position_data[chart_uuids[311]]["parents"] = ["ROOT_ID", "GRID_ID", row3_id]

    # 4. Update the dashboard with the position_json
    print(f"Updating dashboard {dashboard_id} with chart layout...")
    try:
        update_payload = {
            "dashboard_title": existing_dashboard["dashboard_title"],
            "css": existing_dashboard["css"],
            "json_metadata": existing_dashboard["json_metadata"],
            "owners": [owner["id"] for owner in existing_dashboard.get("owners", [])],
            "position_json": json.dumps(position_data),
            "published": existing_dashboard["published"],
            "slug": existing_dashboard.get("slug"),
        }
        client.update_dashboard(dashboard_id, update_payload)
        print(f"Successfully updated dashboard {dashboard_id} with chart layout.")
    except Exception as e:
        print(f"!!! Failed to update dashboard {dashboard_id} layout: {e}", file=sys.stderr)

if __name__ == "__main__":
    create_ga_dashboard()