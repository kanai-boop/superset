import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

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
        # Set Authorization header for subsequent requests
        self._session.headers.update({"Authorization": f"Bearer {self._access_token}"})

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.config.base_url}{path}"
        resp = self._session.request(method, url, timeout=60, **kwargs)
        # Raise detailed error if possible
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            detail = None
            try:
                detail = resp.json()
            except Exception:
                pass
            if detail:
                raise requests.HTTPError(f"{e}\nResponse JSON: {detail}") from e
            raise
        return resp

    # Dataset endpoints
    def get_dataset(self, dataset_id: int) -> Dict[str, Any]:
        return self._request("GET", f"/api/v1/dataset/{dataset_id}").json()["result"]

    def get_dataset_columns(self, dataset_id: int) -> Dict[str, Any]:
        return self._request("GET", f"/api/v1/dataset/{dataset_id}?q=(columns:!)").json()["result"]

    def refresh_dataset(self, dataset_id: int) -> Dict[str, Any]:
        # Sync columns from source
        return self._request("PUT", f"/api/v1/dataset/{dataset_id}/refresh").json()

    def update_dataset(self, dataset_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PUT", f"/api/v1/dataset/{dataset_id}", json=payload).json()

    # Chart endpoints
    def get_chart(self, chart_id: int) -> Dict[str, Any]:
        return self._request("GET", f"/api/v1/chart/{chart_id}").json()["result"]

    def update_chart(self, chart_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PUT", f"/api/v1/chart/{chart_id}", json=payload).json()

    def delete_chart(self, chart_id: int) -> Dict[str, Any]:
        return self._request("DELETE", f"/api/v1/chart/{chart_id}").json()

    def create_chart(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/api/v1/chart/", json=payload).json()

    # Dashboard endpoints
    def get_dashboard(self, dashboard_id: int) -> Dict[str, Any]:
        return self._request("GET", f"/api/v1/dashboard/{dashboard_id}").json()["result"]

    def update_dashboard(self, dashboard_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PUT", f"/api/v1/dashboard/{dashboard_id}", json=payload).json()

    def delete_dashboard(self, dashboard_id: int) -> Dict[str, Any]:
        return self._request("DELETE", f"/api/v1/dashboard/{dashboard_id}").json()

