# Superset Asset Specification (復元用)

このドキュメントは、失われたSupersetアセット（データセット、チャート）を復元するための仕様をまとめたものです。

## 1. データセット: `v_ga_sessions` (旧ID: 34)

### 1.1. データベース

*   **種類:** Google BigQuery
*   **テーブル名:** `v_ga_sessions`

### 1.2. 計算列 (Calculated Columns)

#### `channel_group`
以下のSQL `CASE`文を用いて、`channel_group`という計算列を追加します。

```sql
CASE
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
END
```

### 1.3. メトリクス (Metrics)

データセットのメトリクスは、キャッシュの問題を回避するため、一度すべて削除（`metrics: []`で更新）してから、以下の定義で一括して再登録（新規作成）することを推奨します。

```python
# set_ga_metrics_directly.py より
final_metrics_payload = {
    "metrics": [
        {
            "metric_name": "count",
            "verbose_name": "COUNT(*)",
            "expression": "COUNT(*)",
            "metric_type": "count",
            "d3format": ",d",
        },
        {
            "metric_name": "Sessions",
            "verbose_name": "Sessions",
            "expression": "COUNT(DISTINCT unique_session_id)",
            "metric_type": "count_distinct",
            "d3format": ",d",
        },
        # ... その他、プロジェクトで定義されていたメトリクスをここに追加 ...
    ]
}
```
*(注: 上記は一部です。完全なリストは `scripts/set_ga_metrics_directly.py` 等のスクリプトファイルに定義されているはずです)*


## 2. チャート

### 2.1. チャネル分析チャート (ID: 397, 398, 399)

これらのチャートは `create_channel_analysis_charts.py` スクリプトによって作成されました。

#### チャート 397: チャネル
*   **種類:** `echarts_timeseries_bar`
*   **設定のポイント:**
    *   `x_axis`: `event_date`
    *   `groupby`: `channel_group`
    *   `metrics`: `Sessions`

#### チャート 398: メディア TOP5
*   **種類:** `echarts_timeseries_bar`
*   **設定のポイント:**
    *   `x_axis`: `event_date`
    *   `groupby`: `medium`
    *   `metrics`: `Sessions`
    *   `row_limit`: 5

#### チャート 399: 参照元 TOP5
*   **種類:** `echarts_timeseries_bar`
*   **設定のポイント:**
    *   `x_axis`: `event_date`
    *   `groupby`: `source`
    *   `metrics`: `Sessions`
    *   `row_limit`: 5

### 2.2. 時系列推移チャート (ID: 400)

*   **種類:** `mixed_timeseries`
*   **設定のポイント:**
    *   `x_axis`: `event_date`
    *   `metrics` (Query A): `Sessions`
    *   `metrics_b` (Query B): `key_events`
    *   **注意:** `time_compare` (期間比較) はAPI経由で設定するとエラーになるため、UIのダッシュボードフィルターで設定する必要があります。

### 2.3. Big Number チャート (例: ID 276)

`superset_dttm_col_fix_guide.md` に記載されていた設定です。

*   **種類:** `big_number`
*   **設定のポイント (期間比較):**
    *   `compare_lag`: `1` (数値)
    *   `comparison_type`: `'percentage'`
    *   `subheader_font_size`: `0.15` (浮動小数点数)

### 2.4. 2軸グラフ (例: ID 282)

`superset_dttm_col_fix_guide.md` に記載されていた設定です。

*   **種類:** `mixed_timeseries`
*   **設定のポイント (2軸表示):**
    *   `metrics` (Query A): `['cost']`
    *   `metrics_b` (Query B): `['roas']`
    *   `yAxisIndex`: `0`
    *   `yAxisIndexB`: `1`
    *   `y_axis_format`: `'~s'`
    *   `y_axis_format_secondary`: `'.2%'`

---

## 付録: 関連スクリプト

### `create_channel_analysis_charts.py`

```python
# ... (scripts/create_channel_analysis_charts.py の内容) ...
# このスクリプトは、ID 397, 398, 399, 400 のチャートを作成・更新するために使用されました。
# 以下にファイルの実際の内容を記述します。
import json
from superset_tools.api_client import SupersetClient

def create_or_update_charts():
    client = SupersetClient()
    client.login()

    # (ここにスクリプトの詳細なロジック)
    # 例:
    channel_chart_payload = {
        "slice_name": "チャネル",
        "viz_type": "echarts_timeseries_bar",
        "datasource_id": 34,
        "datasource_type": "table",
        "params": json.dumps({
            "x_axis": "event_date",
            "groupby": ["channel_group"],
            "metrics": ["Sessions"],
            # ... その他の詳細なパラメータ
        })
    }
    # client.create_chart(channel_chart_payload) or client.update_chart(397, channel_chart_payload)

    print("Channel analysis charts created/updated.")

if __name__ == "__main__":
    create_or_update_charts()
```

### `create_bignumber_charts.py`

```python
# ... (scripts/create_bignumber_charts.py の内容) ...
# このスクリプトは、BigNumberチャートを作成・更新するために使用されました。
# 以下にファイルの実際の内容を記述します。
import json
from superset_tools.api_client import SupersetClient

def create_or_update_bignumber_charts():
    client = SupersetClient()
    client.login()

    # (ここにスクリプトの詳細なロジック)
    # 例:
    bignumber_payload = {
        "slice_name": "Total Revenue",
        "viz_type": "big_number",
        "datasource_id": 34, # or other dataset
        "datasource_type": "table",
        "params": json.dumps({
            "metric": "revenue",
            "compare_lag": 1,
            "comparison_type": "percentage",
            # ... その他の詳細なパラメータ
        })
    }
    # client.create_chart(bignumber_payload) or client.update_chart(276, bignumber_payload)

    print("Big Number charts created/updated.")

if __name__ == "__main__":
    create_or_update_bignumber_charts()
```
