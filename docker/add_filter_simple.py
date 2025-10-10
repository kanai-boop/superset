
import sys
import requests
import os
import json
import uuid

def main():
    if len(sys.argv) < 3:
        print("Usage: python add_filter_simple.py <dashboard_id> <dataset_id:column_name>")
        return 1

    dashboard_id = sys.argv[1]
    try:
        ds_id_str, col_name = sys.argv[2].split(":", 1)
        ds_id = int(ds_id_str)
    except ValueError:
        print(f"Invalid dataset argument: {sys.argv[2]}")
        return 1

    base_url = os.environ.get("SUPERSET_BASE_URL", "http://localhost:8088")
    username = os.environ.get("SUPERSET_USERNAME", "admin")
    password = os.environ.get("SUPERSET_PASSWORD", "admin")

    session = requests.Session()

    # 1. Login
    try:
        resp = session.post(f"{base_url}/api/v1/security/login", json={
            "username": username, "password": password, "provider": "db"
        })
        resp.raise_for_status()
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    except requests.exceptions.RequestException as e:
        print(f"Failed to login: {e}", file=sys.stderr)
        return 1

    # 2. Get current dashboard config
    try:
        resp = session.get(f"{base_url}/api/v1/dashboard/{dashboard_id}", headers=headers)
        resp.raise_for_status()
        dash = resp.json()["result"]
    except requests.exceptions.RequestException as e:
        print(f"Failed to get dashboard: {e}", file=sys.stderr)
        return 1

    # 3. Add new filter to metadata
    try:
        jm = json.loads(dash.get("json_metadata") or "{}")
    except json.JSONDecodeError:
        jm = {}
    
    nfc = jm.get("native_filter_configuration", [])
    
    # Avoid adding duplicate filters
    for existing_filter in nfc:
        for target in existing_filter.get("targets", []):
            if target.get("datasetId") == ds_id and target.get("column", {}).get("name") == col_name:
                print(f"Filter for {ds_id}:{col_name} already exists.")
                return 0

    filter_id = f"NATIVE_FILTER-{uuid.uuid4()}"
    region_filter = {
        "id": filter_id,
        "name": "Region",
        "filterType": "filter_select",
        "targets": [{"datasetId": ds_id, "column": {"name": col_name}}],
        "defaultDataMask": {"filterState": {"value": None}},
        "cascadeParentIds": [],
        "scope": {"rootPath": [], "excluded": []},
        "controlValues": {"enableEmptyFilter": True, "multiSelect": True},
    }
    nfc.append(region_filter)
    jm["native_filter_configuration"] = nfc

    # 4. Update dashboard
    owner_ids = [o["id"] for o in dash.get("owners", [])]
    payload = {
        "json_metadata": json.dumps(jm),
        # Include other required fields from the original dashboard object
        "dashboard_title": dash.get("dashboard_title"),
        "slug": dash.get("slug"),
        "owners": owner_ids,
        "position_json": dash.get("position_json"),
        "css": dash.get("css"),
        "published": dash.get("published"),
    }

    try:
        resp = session.put(f"{base_url}/api/v1/dashboard/{dashboard_id}", headers=headers, json=payload)
        resp.raise_for_status()
        print(f"Successfully added Region filter to dashboard {dashboard_id}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to update dashboard: {e}", file=sys.stderr)
        print(resp.text, file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
