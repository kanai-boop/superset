import json
from superset_tools.api_client import SupersetClient

def create_missing_charts():
    """Creates the remaining charts as defined in superset_asset_spec.md"""
    client = SupersetClient()
    client.login()

    # --- Chart Definitions ---
    v_ga_sessions_id = 26
    v_ga_ads_performance_id = 27

    # 1. Time Series Bar Chart: Channel over time
    print("--- Creating Chart 1: GA: チャネル別 時系列 ---")
    channel_timeseries_params = {
        "viz_type": "echarts_timeseries_bar",
        "datasource": f"{v_ga_sessions_id}__table",
        "x_axis": "session_date",
        "metrics": ["Sessions"],
        "groupby": ["channel_group"],
        "time_grain_sqla": "P1D",
        "stack": True,
        "row_limit": 10000,
        "rich_tooltip": True,
    }
    channel_timeseries_payload = {
        "slice_name": "GA: チャネル別 時系列",
        "viz_type": "echarts_timeseries_bar",
        "datasource_id": v_ga_sessions_id,
        "datasource_type": "table",
        "params": json.dumps(channel_timeseries_params),
    }
    try:
        client.create_chart(channel_timeseries_payload)
        print("Successfully created 'GA: チャネル別 時系列'")
    except Exception as e:
        print(f"Chart 'GA: チャネル別 時系列' might already exist or failed: {e}")

    # 2. Time Series Bar Chart: Medium Top 5
    print("--- Creating Chart 2: GA: メディア別 時系列 TOP5 ---")
    medium_timeseries_params = {
        "viz_type": "echarts_timeseries_bar",
        "datasource": f"{v_ga_sessions_id}__table",
        "x_axis": "session_date",
        "metrics": ["Sessions"],
        "groupby": ["medium"],
        "time_grain_sqla": "P1D",
        "stack": True,
        "row_limit": 5,
        "rich_tooltip": True,
    }
    medium_timeseries_payload = {
        "slice_name": "GA: メディア別 時系列 TOP5",
        "viz_type": "echarts_timeseries_bar",
        "datasource_id": v_ga_sessions_id,
        "datasource_type": "table",
        "params": json.dumps(medium_timeseries_params),
    }
    try:
        client.create_chart(medium_timeseries_payload)
        print("Successfully created 'GA: メディア別 時系列 TOP5'")
    except Exception as e:
        print(f"Chart 'GA: メディア別 時系列 TOP5' might already exist or failed: {e}")

    # 3. Time Series Bar Chart: Source Top 5
    print("--- Creating Chart 3: GA: 参照元別 時系列 TOP5 ---")
    source_timeseries_params = {
        "viz_type": "echarts_timeseries_bar",
        "datasource": f"{v_ga_sessions_id}__table",
        "x_axis": "session_date",
        "metrics": ["Sessions"],
        "groupby": ["source"],
        "time_grain_sqla": "P1D",
        "stack": True,
        "row_limit": 5,
        "rich_tooltip": True,
    }
    source_timeseries_payload = {
        "slice_name": "GA: 参照元別 時系列 TOP5",
        "viz_type": "echarts_timeseries_bar",
        "datasource_id": v_ga_sessions_id,
        "datasource_type": "table",
        "params": json.dumps(source_timeseries_params),
    }
    try:
        client.create_chart(source_timeseries_payload)
        print("Successfully created 'GA: 参照元別 時系列 TOP5'")
    except Exception as e:
        print(f"Chart 'GA: 参照元別 時系列 TOP5' might already exist or failed: {e}")

    # 4. Mixed Time Series: Sessions vs Conversions
    print("--- Creating Chart 4: GA: セッション vs コンバージョン 時系列 ---")
    mixed_timeseries_params = {
        "viz_type": "mixed_timeseries",
        "datasource": f"{v_ga_sessions_id}__table",
        "x_axis": "session_date",
        "time_grain_sqla": "P1D",
        "metrics": ["Sessions"],
        "metrics_b": ["Conversions"],
        "y_axis_format": ",d",
        "y_axis_format_secondary": ",d",
        "row_limit": 10000,
    }
    mixed_timeseries_payload = {
        "slice_name": "GA: セッション vs コンバージョン 時系列",
        "viz_type": "mixed_timeseries",
        "datasource_id": v_ga_sessions_id,
        "datasource_type": "table",
        "params": json.dumps(mixed_timeseries_params),
    }
    try:
        client.create_chart(mixed_timeseries_payload)
        print("Successfully created 'GA: セッション vs コンバージョン 時系列'")
    except Exception as e:
        print(f"Chart 'GA: セッション vs コンバージョン 時系列' might already exist or failed: {e}")

    # 5. Big Number Chart: Total Sessions
    print("--- Creating Chart 5: GA: 総セッション数 (Big Number) ---")
    total_sessions_bignumber_params = {
        "viz_type": "big_number",
        "datasource": f"{v_ga_sessions_id}__table",
        "metric": "Sessions",
        "compare_lag": 1,
        "comparison_type": "percentage",
        "subheader_font_size": 0.15,
        "show_delta": True,
        "show_percent": True,
    }
    total_sessions_bignumber_payload = {
        "slice_name": "GA: 総セッション数 (Big Number)",
        "viz_type": "big_number",
        "datasource_id": v_ga_sessions_id,
        "datasource_type": "table",
        "params": json.dumps(total_sessions_bignumber_params),
    }
    try:
        client.create_chart(total_sessions_bignumber_payload)
        print("Successfully created 'GA: 総セッション数 (Big Number)'")
    except Exception as e:
        print(f"Chart 'GA: 総セッション数 (Big Number)' might already exist or failed: {e}")

    # 6. Dual-axis Chart: Cost vs ROAS
    print("--- Creating Chart 6: GA: コスト vs ROAS (2軸グラフ) ---")
    cost_roas_dual_axis_params = {
        "viz_type": "mixed_timeseries",
        "datasource": f"{v_ga_ads_performance_id}__table",
        "x_axis": "date", # Assuming 'date' is the temporal column in v_ga_ads_performance
        "time_grain_sqla": "P1D",
        "metrics": ["cost"],
        "metrics_b": ["roas"],
        "yAxisIndex": 0,
        "yAxisIndexB": 1,
        "y_axis_format": "~s",
        "y_axis_format_secondary": ".2%",
        "row_limit": 10000,
    }
    cost_roas_dual_axis_payload = {
        "slice_name": "GA: コスト vs ROAS (2軸グラフ)",
        "viz_type": "mixed_timeseries",
        "datasource_id": v_ga_ads_performance_id,
        "datasource_type": "table",
        "params": json.dumps(cost_roas_dual_axis_params),
    }
    try:
        client.create_chart(cost_roas_dual_axis_payload)
        print("Successfully created 'GA: コスト vs ROAS (2軸グラフ)'")
    except Exception as e:
        print(f"Chart 'GA: コスト vs ROAS (2軸グラフ)' might already exist or failed: {e}")

if __name__ == "__main__":
    create_missing_charts()
