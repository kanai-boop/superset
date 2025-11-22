import json
import sys
import os
import base64
from pathlib import Path

# Ensure the script can find the API client
sys.path.append(str(Path(__file__).parent.parent))
from scripts.superset_tools.api_client import SupersetClient

class SupersetAssetRestorer:
    """
    Restores Superset database, datasets, and charts from predefined specifications.
    """

    def __init__(self):
        self.client = SupersetClient()
        self.bigquery_db_id = None
        self.ga_sessions_dataset_id = None
        self.ads_performance_dataset_id = None

    def login(self):
        """Logs in to the Superset API."""
        print("--- Logging in to Superset API... ---")
        self.client.login()
        print("Login successful.")

    def create_bigquery_database(self):
        """Creates the BigQuery database connection in Superset, assuming ADC is set."""
        print("--- Creating BigQuery database connection (using Application Default Credentials)... ---")

        # First, check if the database already exists to avoid duplicates
        try:
            response = self.client.list_databases()
            databases = response.get("result", [])
            for db in databases:
                if db.get("database_name") == "BigQuery GA Data":
                    self.bigquery_db_id = db["id"]
                    print(f"BigQuery database 'BigQuery GA Data' already exists with ID: {self.bigquery_db_id}. Skipping creation.")
                    return
        except Exception as e:
            print(f"Warning: Could not check for existing databases: {e}", file=sys.stderr)

        # If not found, create it.
        # No 'extra' field is needed; the backend will use the GOOGLE_APPLICATION_CREDENTIALS
        # environment variable set in the container.
        payload = {
            "database_name": "BigQuery GA Data",
            "sqlalchemy_uri": "bigquery://winglish-gemini-cli"
        }

        try:
            resp = self.client._request("POST", "/api/v1/database/", json=payload)
            self.bigquery_db_id = resp.json()["id"]
            print(f"Successfully created BigQuery database 'BigQuery GA Data' with ID: {self.bigquery_db_id}")
        except Exception as e:
            print(f"!!! Critical error: Could not create BigQuery database: {e}", file=sys.stderr)
            sys.exit(1)

    def create_datasets(self):
        """Creates the necessary datasets."""
        if not self.bigquery_db_id:
            print("!!! Critical error: BigQuery Database ID not found. Cannot create datasets.", file=sys.stderr)
            sys.exit(1)
            
        print("--- Creating datasets... ---")
        self._create_dataset("v_ga_sessions", "ga_sessions_dataset_id")
        self._create_dataset("v_ga_ads_performance", "ads_performance_dataset_id")

    def _create_dataset(self, table_name, id_attribute):
        """Helper to create a single dataset."""
        print(f"Creating dataset for table: {table_name}...")
        payload = {
            "database": self.bigquery_db_id,
            "table_name": table_name,
            "schema": "analytics_456071139",
        }
        try:
            resp = self.client.create_dataset(payload)
            dataset_id = resp["id"]
            setattr(self, id_attribute, dataset_id)
            print(f"Successfully created dataset '{table_name}' with ID: {dataset_id}")
        except Exception as e:
            print(f"!!! Failed to create dataset '{table_name}': {e}", file=sys.stderr)
            sys.exit(1)

    def update_ga_sessions_dataset(self):
        """Adds calculated columns and metrics to the v_ga_sessions dataset."""
        if not self.ga_sessions_dataset_id:
            print("!!! Skipping update for v_ga_sessions: dataset ID not found.", file=sys.stderr)
            return

        print(f"--- Updating dataset ID: {self.ga_sessions_dataset_id} (v_ga_sessions) ---")

        # 1. Add Calculated Column
        print("Adding calculated column: channel_group...")
        channel_group_sql = """CASE
  WHEN ((source = 'google' AND medium = 'organic') OR source = 'yahoo' AND medium = 'organic') THEN 'Organic Search'
  WHEN (source = 'google' AND medium = 'cpc') THEN 'Paid Search'
  WHEN (source = 'facebook' AND medium = 'cpc') THEN 'Paid Social'
  WHEN (source = 'bing' AND medium = 'cpc') THEN 'Paid Search'
  WHEN (source = 'twitter' AND medium = 'cpc') THEN 'Paid Social'
  WHEN (source = 'instagram' AND medium = 'cpc') THEN 'Paid Social'
  WHEN (source = 'line' AND medium = 'cpc') THEN 'Paid Social'
  WHEN (source = 'youtube' AND medium = 'cpc') THEN 'Paid Video'
  WHEN medium = 'display' THEN 'Display'
  WHEN medium = 'video' THEN 'Paid Video'
  WHEN medium = 'social' THEN 'Organic Social'
  WHEN medium = 'email' THEN 'Email'
  WHEN medium = 'referral' THEN 'Referral'
  WHEN source = '(direct)' THEN 'Direct'
  ELSE 'Other'
END"""
        try:
            existing_dataset = self.client.get_dataset(self.ga_sessions_dataset_id, q={"columns": ["columns"]})
            existing_columns = existing_dataset.get("columns", [])
            
            if not any(c['column_name'] == 'channel_group' for c in existing_columns):
                new_column = {
                    "column_name": "channel_group",
                    "verbose_name": "Channel Group",
                    "expression": channel_group_sql,
                    "is_dttm": False,
                    "type": "STRING",
                }
                update_payload = {"columns": existing_columns + [new_column]}
                self.client.update_dataset(self.ga_sessions_dataset_id, update_payload)
                print("Successfully added calculated column 'channel_group'.")
            else:
                print("'channel_group' column already exists.")
        except Exception as e:
            print(f"!!! Failed to add calculated column: {e}", file=sys.stderr)

        # 2. Overwrite Metrics
        print("Overwriting metrics...")
        metrics_payload = {
            "metrics": [
                {"metric_name": "count", "verbose_name": "COUNT(*)", "expression": "COUNT(*)", "metric_type": "count", "d3format": ",d"},
                {"metric_name": "Sessions", "verbose_name": "Sessions", "expression": "COUNT(DISTINCT unique_session_id)", "metric_type": "count_distinct", "d3format": ",d"},
                {"metric_name": "Users", "verbose_name": "Users", "expression": "COUNT(DISTINCT user_pseudo_id)", "metric_type": "count_distinct", "d3format": ",d"},
                {"metric_name": "Revenue", "verbose_name": "Revenue", "expression": "SUM(revenue)", "metric_type": "sum", "d3format": "¥,.0f"},
                {"metric_name": "Conversions", "verbose_name": "Conversions", "expression": "SUM(conversions)", "metric_type": "sum", "d3format": ",d"},
                {"metric_name": "Conversion Rate", "verbose_name": "Conversion Rate", "expression": "SUM(conversions) / NULLIF(COUNT(DISTINCT unique_session_id), 0)", "metric_type": "expression", "d3format": ".2%"},
                {"metric_name": "AOV", "verbose_name": "AOV (Average Order Value)", "expression": "SUM(revenue) / NULLIF(SUM(conversions), 0)", "metric_type": "expression", "d3format": "¥,.0f"},
                {"metric_name": "Avg Engagement Time (sec)", "verbose_name": "Avg Engagement Time (sec)", "expression": "AVG(total_engagement_time_msec) / 1000", "metric_type": "expression", "d3format": ",.1fS"},
                {"metric_name": "Bounce Rate (Proxy)", "verbose_name": "Bounce Rate (Proxy)", "expression": "1 - (SUM(CASE WHEN is_engaged_session THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT unique_session_id), 0))", "metric_type": "expression", "d3format": ".2%"},
                {"metric_name": "Engaged Sessions", "verbose_name": "Engaged Sessions", "expression": "SUM(CASE WHEN is_engaged_session THEN 1 ELSE 0 END)", "metric_type": "sum", "d3format": ",d"},
            ]
        }
        try:
            self.client.update_dataset(self.ga_sessions_dataset_id, metrics_payload)
            print(f"Successfully set {len(metrics_payload['metrics'])} metrics.")
        except Exception as e:
            print(f"!!! Failed to set metrics: {e}", file=sys.stderr)

    def create_charts(self):
        """Creates all the necessary charts."""
        print("--- Creating charts... ---")
        self._create_channel_analysis_charts()
        self._create_bignumber_charts()

    def _create_channel_analysis_charts(self):
        if not self.ga_sessions_dataset_id:
            print("!!! Skipping channel analysis charts: v_ga_sessions dataset ID not found.", file=sys.stderr)
            return
        
        print("Creating channel analysis charts...")
        bar_charts_to_create = [
            {"slice_name": "チャネル", "groupby": ["channel_group"], "row_limit": 100, "y_axis_label": "Channel"},
            {"slice_name": "メディア TOP5", "groupby": ["medium"], "row_limit": 5, "y_axis_label": "Medium"},
            {"slice_name": "参照元 TOP5", "groupby": ["source"], "row_limit": 5, "y_axis_label": "Source"},
        ]

        for chart_def in bar_charts_to_create:
            params = {
                "viz_type": "bar",
                "metrics": ["Users", "Sessions", "Conversions"],
                "groupby": chart_def["groupby"],
                "adhoc_filters": [],
                "row_limit": chart_def["row_limit"],
                "rich_tooltip": True,
                "orientation": "horizontal",
                "y_axis_label": chart_def["y_axis_label"],
                "x_axis_label": "Count",
                "time_range_endpoints": ["inclusive", "exclusive"],
            }
            payload = {
                "slice_name": chart_def["slice_name"],
                "viz_type": "bar",
                "datasource_id": self.ga_sessions_dataset_id,
                "datasource_type": "table",
                "params": json.dumps(params),
            }
            self._create_chart_from_payload(payload)

    def _create_bignumber_charts(self):
        if not self.ads_performance_dataset_id:
            print("!!! Skipping big number charts: v_ga_ads_performance dataset ID not found.", file=sys.stderr)
            return

        print("Creating big number charts...")
        chart_configs = [
            {"slice_name": "CPA", "metric": "cpa", "y_axis_format": ",.0f", "currency": {"symbol": "JPY", "symbolPosition": "prefix"}},
            {"slice_name": "CPC", "metric": "cpc", "y_axis_format": ",.0f", "currency": {"symbol": "JPY", "symbolPosition": "prefix"}},
            {"slice_name": "CVR", "metric": "cvr", "y_axis_format": ".2%"},
            {"slice_name": "CPM", "metric": "cpm", "y_axis_format": ",.0f", "currency": {"symbol": "JPY", "symbolPosition": "prefix"}},
        ]

        for config in chart_configs:
            params = {
                "metric": config["metric"],
                "y_axis_format": config["y_axis_format"],
                "compare_lag": 1,
                "comparison_type": "percentage",
                "subheader_font_size": 0.15,
                "show_delta": True,
                "show_percent": True,
            }
            if "currency" in config:
                params["currency_format"] = config["currency"]

            payload = {
                "slice_name": config["slice_name"],
                "viz_type": "big_number",
                "datasource_id": self.ads_performance_dataset_id,
                "datasource_type": "table",
                "params": json.dumps(params),
            }
            self._create_chart_from_payload(payload)

    def _create_chart_from_payload(self, payload):
        """Helper to create a single chart from a prepared payload."""
        slice_name = payload['slice_name']
        print(f"Creating chart: {slice_name}...")
        try:
            resp = self.client.create_chart(payload)
            chart_id = resp["id"]
            print(f"Successfully created chart '{slice_name}' with ID: {chart_id}")
        except Exception as e:
            print(f"!!! Failed to create chart '{slice_name}': {e}", file=sys.stderr)

    def run(self):
        """Executes the full restoration workflow."""
        self.login()
        # The script uses the GOOGLE_APPLICATION_CREDENTIALS environment variable.
        self.create_bigquery_database()
        self.create_datasets()
        self.update_ga_sessions_dataset()
        self.create_charts()
        print("\n--- Asset restoration process complete. ---")

if __name__ == "__main__":
    restorer = SupersetAssetRestorer()
    restorer.run()
