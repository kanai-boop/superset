
import sys
import requests
import os
import json

# --- Chart Definitions ---
CHARTS_TO_CREATE = [
    # Big Numbers
    {'slice_name': 'Total Conversions', 'viz_type': 'big_number', 'dataset_name': 'p_ads_CampaignStats_9535431119', 'params': {'metric': 'conversions', 'y_axis_format': ',.0f'}},
    {'slice_name': 'Total Cost', 'viz_type': 'big_number', 'dataset_name': 'p_ads_CampaignStats_9535431119', 'params': {'metric': 'cost', 'y_axis_format': '$,.2f'}},
    {'slice_name': 'ROAS', 'viz_type': 'big_number', 'dataset_name': 'p_ads_CampaignStats_9535431119', 'params': {'metric': 'roas', 'y_axis_format': '.2%'}},
    {'slice_name': 'CTR', 'viz_type': 'big_number', 'dataset_name': 'p_ads_CampaignStats_9535431119', 'params': {'metric': 'ctr', 'y_axis_format': '.2%'}},
    {'slice_name': 'Total Clicks', 'viz_type': 'big_number', 'dataset_name': 'p_ads_CampaignStats_9535431119', 'params': {'metric': 'clicks', 'y_axis_format': ',.0f'}},
    {'slice_name': 'Total Impressions', 'viz_type': 'big_number', 'dataset_name': 'p_ads_CampaignStats_9535431119', 'params': {'metric': 'impressions', 'y_axis_format': ',.0f'}},
    # Mixed Time-Series
    {'slice_name': 'Financial Trends (Daily)', 'viz_type': 'mixed_timeseries', 'dataset_name': 'p_ads_CampaignStats_9535431119', 'params': {'granularity_sqla': 'segments_date', 'time_grain_sqla': 'P1D', 'metrics': ['cost'], 'metrics_b': ['roas']}},
    {'slice_name': 'Traffic Trends (Daily)', 'viz_type': 'mixed_timeseries', 'dataset_name': 'p_ads_CampaignStats_9535431119', 'params': {'granularity_sqla': 'segments_date', 'time_grain_sqla': 'P1D', 'metrics': ['clicks', 'impressions'], 'metrics_b': ['ctr']}},
    # Tables
    {'slice_name': 'Campaign Performance', 'viz_type': 'table', 'dataset_name': 'p_ads_CampaignStats_9535431119', 'params': {'groupby': ['campaign_base_campaign'], 'metrics': ['cost', 'clicks', 'impressions', 'ctr', 'conversions', 'cpa', 'roas'], 'all_columns': ['campaign_base_campaign']}},
    {'slice_name': 'Landing Page Performance', 'viz_type': 'table', 'dataset_name': 'v_landing_page_performance_with_device_and_medium', 'params': {'groupby': ['landing_page', 'device_category', 'traffic_medium'], 'metrics': ['sessions', 'users'], 'all_columns': ['landing_page', 'device_category', 'traffic_medium', 'sessions', 'users']}},
]

def get_dataset_id(session, base_url, headers, dataset_name):
    try:
        query = {"filters":[{"col":"table_name","opr":"eq","value":dataset_name}]}
        resp = session.get(f"{base_url}/api/v1/dataset/?q={json.dumps(query)}", headers=headers)
        resp.raise_for_status()
        results = resp.json()["result"]
        if not results:
            print(f"Error: Dataset '{dataset_name}' not found.", file=sys.stderr)
            return None
        return results[0]["id"]
    except Exception as e:
        print(f"Error finding dataset {dataset_name}: {e}", file=sys.stderr)
        return None

def main():
    base_url = os.environ.get("SUPERSET_BASE_URL", "http://localhost:8088")
    username = os.environ.get("SUPERSET_USERNAME", "admin")
    password = os.environ.get("SUPERSET_PASSWORD", "admin")

    session = requests.Session()
    try:
        resp = session.post(f"{base_url}/api/v1/security/login", json={"username": username, "password": password, "provider": "db"})
        resp.raise_for_status()
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    except requests.exceptions.RequestException as e:
        print(f"Failed to login: {e}", file=sys.stderr)
        return 1

    dataset_ids = {}
    for chart_def in CHARTS_TO_CREATE:
        ds_name = chart_def['dataset_name']
        if ds_name not in dataset_ids:
            dataset_ids[ds_name] = get_dataset_id(session, base_url, headers, ds_name)
            if not dataset_ids[ds_name]:
                return 1

    print("--- Creating Charts ---")
    for chart_def in CHARTS_TO_CREATE:
        ds_name = chart_def['dataset_name']
        ds_id = dataset_ids[ds_name]
        
        payload = {
            "datasource_id": ds_id,
            "datasource_type": "table",
            "slice_name": chart_def['slice_name'],
            "viz_type": chart_def['viz_type'],
            "params": json.dumps(chart_def['params'])
        }

        try:
            resp = session.post(f"{base_url}/api/v1/chart/", headers=headers, json=payload)
            resp.raise_for_status()
            response_data = resp.json()
            chart_id = response_data['id']
            slice_name = response_data['result']['slice_name']
            print(f"Successfully created chart: '{slice_name}' (ID: {chart_id})")
        except requests.exceptions.RequestException as e:
            print(f"Failed to create chart '{chart_def['slice_name']}': {e}", file=sys.stderr)
            print(f"Response body: {resp.text}", file=sys.stderr)

    return 0

if __name__ == "__main__":
    sys.exit(main())
