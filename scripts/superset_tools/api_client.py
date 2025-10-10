import os
from dataclasses import dataclass
from typing import Any, Dict, Optional
import sys
import json
import argparse

import requests


@dataclass
class SupersetConfig:
    base_url: str = os.environ.get("SUPERSET_BASE_URL", "http://localhost:8088")
    username: str = os.environ.get("SUPERSET_USERNAME", "admin")
    password: str = os.environ.get("SUPERSET_PASSWORD", "admin")


class SupersetClient:
    def __init__(self, config: Optional[SupersetConfig] = None):
        self.config = config or SupersetConfig()
        self._session = requests.Session()
        self._access_token: Optional[str] = None

    def login(self) -> None:
        url = f"{self.config.base_url}/api/v1/security/login"
        payload = {
            "username": self.config.username,
            "password": self.config.password,
            "provider": "db",
            "refresh": True,
        }
        resp = self._session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        self._session.headers.update({"Authorization": f"Bearer {self._access_token}"})

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.config.base_url}{path}"
        resp = self._session.request(method, url, timeout=60, **kwargs)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            detail = None
            try:
                detail = resp.json()
            except Exception:
                pass
            if detail:
                raise requests.HTTPError(f"""{e}
Response JSON: {detail}""") from e
            raise
        return resp

    # Database endpoints
    def list_databases(self) -> Dict[str, Any]:
        return self._request("GET", "/api/v1/database/").json()

    # Dataset endpoints
    def create_dataset(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/api/v1/dataset/", json=payload).json()

    def get_dataset(self, dataset_id: int, q: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = {'q': json.dumps(q)} if q else {}
        return self._request("GET", f"/api/v1/dataset/{dataset_id}", params=params).json()

    def update_dataset(self, dataset_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PUT", f"/api/v1/dataset/{dataset_id}", json=payload).json()

    # Chart endpoints
    def create_chart(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/api/v1/chart/", json=payload).json()

    def delete_chart(self, chart_id: int) -> Dict[str, Any]:
        return self._request("DELETE", f"/api/v1/chart/{chart_id}").json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Superset API Client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list_databases command
    subparsers.add_parser("list_databases", help="List all databases")

    # create_dataset command
    create_ds_parser = subparsers.add_parser("create_dataset", help="Create a new dataset")
    create_ds_parser.add_argument("--db_id", required=True, type=int, help="Database ID")
    create_ds_parser.add_argument("--schema", required=True, help="Schema name")
    create_ds_parser.add_argument("--table_name", required=True, help="Table/View name")

    # create_chart command
    create_chart_parser = subparsers.add_parser("create_chart", help="Create a new chart")
    create_chart_parser.add_argument("--payload", required=True, help="JSON payload for the new chart")

    # get_dataset command
    get_ds_parser = subparsers.add_parser("get_dataset", help="Get dataset details")
    get_ds_parser.add_argument("--dataset_id", required=True, type=int, help="Dataset ID")

    # update_dataset command
    update_ds_parser = subparsers.add_parser("update_dataset", help="Update a dataset")
    update_ds_parser.add_argument("--dataset_id", required=True, type=int, help="Dataset ID")
    update_ds_parser.add_argument("--payload", required=True, help="JSON payload for the update")

    # delete_chart command
    delete_chart_parser = subparsers.add_parser("delete_chart", help="Delete a chart")
    delete_chart_parser.add_argument("--chart_id", required=True, type=int, help="Chart ID to delete")

    args = parser.parse_args()

    client = SupersetClient()
    client.login()

    if args.command == "list_databases":
        result = client.list_databases()
        print(json.dumps(result, indent=2))
    elif args.command == "create_dataset":
        payload = {"database": args.db_id, "schema": args.schema, "table_name": args.table_name}
        result = client.create_dataset(payload)
        print(json.dumps(result, indent=2))
    elif args.command == "create_chart":
        payload = json.loads(args.payload)
        result = client.create_chart(payload)
        print(json.dumps(result, indent=2))
    elif args.command == "get_dataset":
        # A 'q' parameter can be used to fetch related data, like columns and metrics
        q = {"columns": ["columns", "metrics"]}
        result = client.get_dataset(args.dataset_id, q=q)
        print(json.dumps(result, indent=2))
    elif args.command == "update_dataset":
        payload = json.loads(args.payload)
        result = client.update_dataset(args.dataset_id, payload)
        print(json.dumps(result, indent=2))
    elif args.command == "delete_chart":
        result = client.delete_chart(args.chart_id)
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)
