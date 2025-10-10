
import sys
import requests
import os
import json

def main():
    dataset_id = 27

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

    # 2. Refresh the dataset
    try:
        put_url = f"{base_url}/api/v1/dataset/{dataset_id}/refresh"
        resp = session.put(put_url, headers=headers)
        resp.raise_for_status()
        print(f"Successfully triggered refresh for dataset {dataset_id}.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to refresh dataset {dataset_id}: {e}", file=sys.stderr)
        print(f"Response body: {resp.text}", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
