# チャートテンプレ（params ひな形）

params は JSON 文字列としてチャート API に渡す。`datasource` は `<DATASET_ID>__table`。

## 1) チャネル別 時系列（Time-series Bar、スタッキング有効）
```json
{
  "viz_type":"echarts_timeseries_bar",
  "datasource":"28__table",
  "x_axis":"session_date",
  "time_grain_sqla":"P1D",
  "metrics":["Sessions"],
  "groupby":["channel_group"],
  "stack":"Stack",
  "row_limit":10000,
  "rich_tooltip":true,
  "showTooltipTotal":true,
  "only_total":true
}
```

## 2) メディア別/参照元別 時系列 TOP5
- `groupby` を `medium` / `source` に切替
- `row_limit: 5`

## 3) セッション vs コンバージョン（mixed_timeseries）
```json
{
  "viz_type":"mixed_timeseries",
  "datasource":"28__table",
  "x_axis":"session_date",
  "time_grain_sqla":"P1D",
  "metrics":["Sessions"],
  "metrics_b":["Conversions"],
  "y_axis_format":",d",
  "y_axis_format_secondary":",d",
  "row_limit":10000
}
```

## 4) Big Number（比較表示）
```json
{
  "viz_type":"big_number",
  "datasource":"28__table",
  "metric":"Sessions",
  "compare_lag":1,
  "comparison_type":"percentage",
  "subheader_font_size":0.15,
  "show_delta":true,
  "show_percent":true
}
```

## 5) コスト vs ROAS（2軸 mixed_timeseries）
```json
{
  "viz_type":"mixed_timeseries",
  "datasource":"27__table",
  "x_axis":"event_date",
  "time_grain_sqla":"P1D",
  "metrics":["ads_cost"],
  "metrics_b":["roas"],
  "yAxisIndex":0,
  "yAxisIndexB":1,
  "y_axis_format":"~s",
  "y_axis_format_secondary":".2%",
  "row_limit":10000
}
```

---

## 6) KPI BigNumber（4指標 × 3期間、SQLフィルター版）
- 指標: `Users`, `New Users`, `Sessions`, `Conversion Rate`
- 期間は `time_range` ではなく `adhoc_filters`（SQL）で制御（BigQuery）
- トレンドは非表示、Δ%は `compare_lag=1`, `comparison_type='percentage'`
- **期間合計を表示するには `aggregation: "sum"` と `granularity_sqla: "event_date"` が必要**

MTD（今月、年/月一致チェックでタイムゾーン問題回避）
```json
{
  "viz_type":"big_number",
  "datasource":"28__table",
  "metric":"Users",
  "aggregation":"sum",
  "granularity_sqla":"event_date",
  "time_grain_sqla":null,
  "subheader_font_size":0.15,
  "show_trend_line":false,
  "compare_lag":1,
  "comparison_type":"percentage",
  "show_delta":true,
  "show_percent":true,
  "time_range":"No filter",
  "adhoc_filters":[{
    "expressionType":"SQL",
    "sqlExpression":"EXTRACT(YEAR FROM event_date) = EXTRACT(YEAR FROM CURRENT_DATE()) AND EXTRACT(MONTH FROM event_date) = EXTRACT(MONTH FROM CURRENT_DATE())",
    "clause":"WHERE"
  }]
}
```

先月
```json
{
  "viz_type":"big_number",
  "datasource":"28__table",
  "metric":"Users",
  "aggregation":"sum",
  "granularity_sqla":"event_date",
  "time_grain_sqla":null,
  "subheader_font_size":0.15,
  "show_trend_line":false,
  "compare_lag":1,
  "comparison_type":"percentage",
  "show_delta":true,
  "show_percent":true,
  "time_range":"No filter",
  "adhoc_filters":[{
    "expressionType":"SQL",
    "sqlExpression":"event_date >= DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH) AND event_date < DATE_TRUNC(CURRENT_DATE(), MONTH)",
    "clause":"WHERE"
  }]
}
```

先々月
```json
{
  "viz_type":"big_number",
  "datasource":"28__table",
  "metric":"Users",
  "aggregation":"sum",
  "granularity_sqla":"event_date",
  "time_grain_sqla":null,
  "subheader_font_size":0.15,
  "show_trend_line":false,
  "compare_lag":1,
  "comparison_type":"percentage",
  "show_delta":true,
  "show_percent":true,
  "time_range":"No filter",
  "adhoc_filters":[{
    "expressionType":"SQL",
    "sqlExpression":"event_date >= DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 2 MONTH), MONTH) AND event_date < DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH)",
    "clause":"WHERE"
  }]
}
```

※ `metric` を `New Users` / `Sessions` / `Conversion Rate` に置き換えることで同様に作成可能。

## 7) PV BigNumber（3期間）
- データセット: `v_ga_page_views`（ID: 33）
- メトリクス: `Pageviews = SUM(page_view)`
- 期間設定は上記KPI BigNumberと同様（`aggregation: "sum"`, `granularity_sqla: "event_date"` 必須）
- **注意**: PV系チャートはデータセット33（`v_ga_page_views`）を使用。データセット28（`v_ga_sessions`）には`Total Pageviews`（セッション内PV合計）も追加済み。

---

## 8) 集客サマリ：横棒チャート（カテゴリ別、非スタッキング）
- **用途**: チャネル/メディア/参照元別に、Users/Sessions/Conversions を横並びで比較
- **viz_type**: `echarts_timeseries_bar`
- **ポイント**: `x_axis` にカテゴリ列、`groupby: []`、`stack: null` で時系列ではなくカテゴリ別集計

### チャネル別（例：ID 176）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "channel_group",
  "groupby": [],
  "metrics": ["Sessions", "Users", "Conversions"],
  "orientation": "horizontal",
  "stack": null,
  "show_legend": true,
  "rich_tooltip": true,
  "showTooltipTotal": true,
  "y_axis_format": "SMART_NUMBER",
  "order_desc": true,
  "timeseries_limit_metric": "Sessions",
  "row_limit": 10000,
  "adhoc_filters": []
}
```

### メディア別 TOP5（例：ID 177）
- `x_axis: "medium"`, `row_limit: 5`

### 参照元 TOP5（例：ID 178）
- `x_axis: "source"`, `row_limit: 5`

---

## 9) 集客サマリ：時系列折れ線（前月比較付き）
- **用途**: Sessions/Conversions の日次推移を前月と比較（薄い色の破線で表示）
- **viz_type**: `echarts_timeseries_line`
- **ポイント**: `time_compare: ["1 month ago"]` で前月比較を有効化、期間フィルターは `"Last month"` など具体的に指定

### 例（ID 175）
```json
{
  "viz_type": "echarts_timeseries_line",
  "datasource": "28__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1D",
  "metrics": ["Sessions", "Conversions"],
  "groupby": [],
  "adhoc_filters": [{
    "clause": "WHERE",
    "subject": "event_date",
    "operator": "TEMPORAL_RANGE",
    "comparator": "Last month",
    "expressionType": "SIMPLE"
  }],
  "comparison_type": "values",
  "time_compare": ["1 month ago"],
  "comparison_color_enabled": true,
  "show_legend": true,
  "rich_tooltip": true,
  "showTooltipTotal": true,
  "row_limit": 10000
}
```

---

## 10) エンゲージメントレポート：BigNumber（6指標 × 3期間）
- 指標: PV数、セッション数、PV数/セッション、平均エンゲージメント時間（秒）、エンゲージメント率、エンゲージセッション数
- 期間・比較設定はKPI BigNumberと同様
- **PV数のみデータセット33（`v_ga_page_views`）、他はデータセット28（`v_ga_sessions`）**

### 上位ページ TOP10（横棒、ID 197）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "33__table",
  "x_axis": "base_url",
  "groupby": [],
  "metrics": ["Pageviews"],
  "orientation": "horizontal",
  "time_grain_sqla": null,
  "show_legend": true,
  "rich_tooltip": true,
  "order_desc": true,
  "timeseries_limit_metric": "Pageviews",
  "row_limit": 10
}
```

### 時系列2軸（PV数 vs 平均エンゲージメント時間、ID 198）
```json
{
  "viz_type": "mixed_timeseries",
  "datasource": "28__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1D",
  "metrics": ["Total Pageviews"],
  "metrics_b": ["Avg Engagement Time (sec)"],
  "yAxisIndex": 0,
  "yAxisIndexB": 1,
  "y_axis_bounds": [1, null],
  "y_axis_format": ",d",
  "y_axis_format_secondary": ",.0f",
  "adhoc_filters": [{
    "clause": "WHERE",
    "subject": "event_date",
    "operator": "TEMPORAL_RANGE",
    "comparator": "Last month",
    "expressionType": "SIMPLE"
  }],
  "adhoc_filters_b": [{
    "clause": "WHERE",
    "subject": "event_date",
    "operator": "TEMPORAL_RANGE",
    "comparator": "Last month",
    "expressionType": "SIMPLE"
  }],
  "comparison_type": "values",
  "time_compare": ["1 month ago"],
  "comparison_color_enabled": true,
  "row_limit": 10000
}
```

### 時系列2軸（Sessions vs エンゲージメント率、ID 199）
- Query A: `Sessions`、Query B: `Engagement Rate`
- `adhoc_filters_b`も同様に設定（両方に期間フィルター）

---

## 11) 離脱率レポート

### ページ別詳細テーブル（ID 202）
```json
{
  "viz_type": "table",
  "datasource": "34__table",
  "query_mode": "aggregate",
  "groupby": ["page_title", "base_url"],
  "metrics": ["Exit Rate", "Total Pageviews", "Total Exits"],
  "adhoc_filters": [],
  "row_limit": 100,
  "order_desc": true
}
```

### 時系列2軸（PV数 vs 離脱率、ID 200）
```json
{
  "viz_type": "mixed_timeseries",
  "datasource": "34__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1D",
  "metrics": ["Total Pageviews"],
  "metrics_b": ["Exit Rate"],
  "yAxisIndex": 0,
  "yAxisIndexB": 1,
  "y_axis_format": ",d",
  "y_axis_format_secondary": ".1%",
  "adhoc_filters": [{
    "clause": "WHERE",
    "subject": "event_date",
    "operator": "TEMPORAL_RANGE",
    "comparator": "Last month",
    "expressionType": "SIMPLE"
  }],
  "adhoc_filters_b": [{
    "clause": "WHERE",
    "subject": "event_date",
    "operator": "TEMPORAL_RANGE",
    "comparator": "Last month",
    "expressionType": "SIMPLE"
  }],
  "show_legend": true,
  "rich_tooltip": true,
  "row_limit": 10000
}
```

### 散布図（PV数 vs 離脱率、ID 203）
```json
{
  "viz_type": "bubble",
  "datasource": "34__table",
  "entity": "page_title",
  "x": "Total Pageviews",
  "y": "Exit Rate",
  "size": "Total Exits",
  "max_bubble_size": 25,
  "adhoc_filters": [],
  "row_limit": 100,
  "show_legend": false,
  "color_scheme": "supersetColors"
}
```

---

## 12) Google Ads パフォーマンス

### KPI BigNumber（今月 vs 先月、ID 258-263）
```json
{
  "viz_type": "big_number",
  "datasource": "27__table",
  "metric": {
    "expressionType": "SQL",
    "sqlExpression": "SUM(ads_cost)",
    "label": "Cost"
  },
  "aggregation": "sum",
  "granularity_sqla": "event_date",
  "time_grain_sqla": null,
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "EXTRACT(YEAR FROM event_date) = EXTRACT(YEAR FROM CURRENT_DATE()) AND EXTRACT(MONTH FROM event_date) = EXTRACT(MONTH FROM CURRENT_DATE())"
  }],
  "compare_lag": "1",
  "compare_suffix": "先月",
  "comparison_type": "percentage",
  "show_trend_line": false,
  "y_axis_format": "$,.0f"
}
```

**8つのKPI（実装版）**:

期間比較あり（10月 vs 9月）:
- Chart 258: 広告費（`SUM(ads_cost)`, format: `¥,.0f`）
- Chart 259: クリック数（`SUM(ads_clicks)`, format: `,d`）
- Chart 260: インプレッション（`SUM(ads_impressions)`, format: `,d`）
- Chart 261: コンバージョン数（`SUM(conversions)`, format: `,d`）
- Chart 263: CPC（`SUM(ads_cost) / NULLIF(SUM(ads_clicks), 0)`, format: `¥,.2f`）
- Chart 272: CVR（`SUM(conversions) / NULLIF(SUM(ads_clicks), 0) * 100`, format: `.2f`）

全期間データ（比較なし）:
- Chart 262: ROAS（`SUM(revenue) / NULLIF(SUM(ads_cost), 0)`, format: `.2f`）
- Chart 271: CPA（`SUM(ads_cost) / NULLIF(SUM(conversions), 0)`, format: `¥,.2f`）

### 日別広告指標（2軸、ID 264）
```json
{
  "viz_type": "mixed_timeseries",
  "datasource": "27__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1D",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "SUM(ads_cost)",
    "label": "Cost"
  }],
  "metrics_b": [{
    "expressionType": "SQL",
    "sqlExpression": "SUM(ads_clicks)",
    "label": "Clicks"
  }],
  "yAxisIndex": 0,
  "yAxisIndexB": 1,
  "y_axis_format": "¥,.0f",
  "y_axis_format_secondary": ",d",
  "adhoc_filters": [{"clause": "WHERE", "subject": "event_date", "operator": "TEMPORAL_RANGE", "comparator": "Last month", "expressionType": "SIMPLE"}],
  "adhoc_filters_b": [{"clause": "WHERE", "subject": "event_date", "operator": "TEMPORAL_RANGE", "comparator": "Last month", "expressionType": "SIMPLE"}]
}
```

### CTR推移（ID 266）
```json
{
  "viz_type": "echarts_timeseries_line",
  "datasource": "27__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1D",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "SUM(ads_clicks) / NULLIF(SUM(ads_impressions), 0) * 100",
    "label": "CTR (%)"
  }],
  "y_axis_format": ".2f"
}
```

### 広告効率分析（Bubble、ID 268）
```json
{
  "viz_type": "bubble",
  "datasource": "27__table",
  "entity": "event_date",
  "x": {"expressionType": "SQL", "sqlExpression": "SUM(ads_cost)", "label": "Cost"},
  "y": {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"},
  "size": {"expressionType": "SQL", "sqlExpression": "SUM(ads_clicks)", "label": "Clicks"},
  "max_bubble_size": 25
}
```

---

## 13) 新規 vs リピーター分析

### 構成比（円グラフ、ID 281）
```json
{
  "viz_type": "pie",
  "datasource": "28__table",
  "groupby": ["new_vs_returning"],
  "metric": {
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  },
  "show_legend": true,
  "color_scheme": "supersetColors"
}
```

### 比較テーブル（ID 282）
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": ["new_vs_returning"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"},
    {"expressionType": "SQL", "sqlExpression": "COUNT(DISTINCT user_pseudo_id)", "label": "Users"},
    {"expressionType": "SQL", "sqlExpression": "SUM(session_pageviews)", "label": "Pageviews"},
    {"expressionType": "SQL", "sqlExpression": "AVG(session_pageviews)", "label": "PV/Session"},
    {"expressionType": "SQL", "sqlExpression": "COUNTIF(session_pageviews = 1) / NULLIF(COUNT(*), 0) * 100", "label": "Bounce Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "AVG(total_engagement_time_msec / 1000)", "label": "Avg Engagement (sec)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions) / NULLIF(COUNT(*), 0) * 100", "label": "CVR (%)"}
  ]
}
```

### 月別推移（積み上げ棒、ID 283）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1M",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  }],
  "groupby": ["new_vs_returning"],
  "stack": "Stack",
  "show_legend": true
}
```

### デバイス別構成（積み上げ棒、ID 284）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "device_category",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  }],
  "groupby": ["new_vs_returning"],
  "stack": "Stack",
  "show_legend": true
}
```

### エンゲージメント比較（横棒、ID 285）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "new_vs_returning",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "AVG(total_engagement_time_msec / 1000)",
    "label": "Avg Engagement (sec)"
  }],
  "orientation": "horizontal",
  "y_axis_format": ".1f"
}
```

### 直帰率比較（横棒、ID 286）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "new_vs_returning",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNTIF(session_pageviews = 1) / NULLIF(COUNT(*), 0) * 100",
    "label": "Bounce Rate (%)"
  }],
  "orientation": "horizontal",
  "y_axis_format": ".1f"
}
```

---

## 14) コンテンツパフォーマンス分析

### 人気コンテンツランキング（横棒、ID 299）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "37__table",
  "x_axis": "page_title",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "SUM(pageviews)",
    "label": "Pageviews"
  }],
  "orientation": "horizontal",
  "row_limit": 15,
  "y_axis_format": ",d",
  "show_legend": false
}
```

### エンゲージメント高いコンテンツ（横棒、ID 300）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "37__table",
  "x_axis": "page_title",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "AVG(avg_engagement_sec)",
    "label": "Avg Engagement (sec)"
  }],
  "orientation": "horizontal",
  "row_limit": 15,
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "pageviews >= 50"
  }],
  "y_axis_format": ".1f",
  "show_legend": false
}
```

### コンテンツ別パフォーマンステーブル（ID 301）
```json
{
  "viz_type": "table",
  "datasource": "37__table",
  "query_mode": "aggregate",
  "groupby": ["page_title"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "SUM(pageviews)", "label": "Pageviews"},
    {"expressionType": "SQL", "sqlExpression": "SUM(unique_users)", "label": "Unique Users"},
    {"expressionType": "SQL", "sqlExpression": "SUM(sessions)", "label": "Sessions"},
    {"expressionType": "SQL", "sqlExpression": "AVG(avg_engagement_sec)", "label": "Avg Engagement (sec)"},
    {"expressionType": "SQL", "sqlExpression": "AVG(exit_rate)", "label": "Exit Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "AVG(session_conversion_rate)", "label": "CVR (%)"}
  ],
  "row_limit": 30,
  "order_desc": true
}
```

### CV貢献度の高いコンテンツ（横棒、ID 302）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "37__table",
  "x_axis": "page_title",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "SUM(total_conversions)",
    "label": "Total Conversions"
  }],
  "orientation": "horizontal",
  "row_limit": 15,
  "y_axis_format": ",d",
  "show_legend": false
}
```

### コンテンツパフォーマンス分析（Bubble、ID 303）
```json
{
  "viz_type": "bubble",
  "datasource": "37__table",
  "entity": "page_title",
  "x": {
    "expressionType": "SQL",
    "sqlExpression": "AVG(avg_engagement_sec)",
    "label": "Avg Engagement (sec)"
  },
  "y": {
    "expressionType": "SQL",
    "sqlExpression": "AVG(session_conversion_rate)",
    "label": "CVR (%)"
  },
  "size": {
    "expressionType": "SQL",
    "sqlExpression": "SUM(pageviews)",
    "label": "Pageviews"
  },
  "max_bubble_size": 25,
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "pageviews >= 30"
  }],
  "row_limit": 50,
  "show_legend": false
}
```

### 月別コンテンツトレンド（折れ線、ID 304）
```json
{
  "viz_type": "echarts_timeseries_line",
  "datasource": "37__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1M",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "SUM(pageviews)",
    "label": "Pageviews"
  }],
  "groupby": ["page_title"],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "page_title IN ('TOPページ | Winglish', '単語帳 ｜ Winglish', '英文解釈 | Winglish', '長文読解 | Winglish', 'Login | Winglish')"
  }],
  "y_axis_format": ",d",
  "show_legend": true,
  "rich_tooltip": true
}
```

### エントリー・エグジット分析（テーブル、ID 305）
```json
{
  "viz_type": "table",
  "datasource": "37__table",
  "query_mode": "aggregate",
  "groupby": ["page_title"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "SUM(entrances)", "label": "Entrances"},
    {"expressionType": "SQL", "sqlExpression": "SUM(exits)", "label": "Exits"},
    {"expressionType": "SQL", "sqlExpression": "AVG(exit_rate)", "label": "Exit Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(pageviews)", "label": "Pageviews"}
  ],
  "row_limit": 20,
  "order_desc": true
}
```

---

## 15) チャネル × セグメント クロス分析

### チャネル × デバイス構成（積み上げ棒、ID 306）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "source",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  }],
  "groupby": ["device_category"],
  "stack": "Stack",
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "source IS NOT NULL"
  }],
  "row_limit": 10,
  "y_axis_format": ",d",
  "show_legend": true
}
```

### チャネル × デバイス詳細（テーブル、ID 307）
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": ["source", "medium", "device_category"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"},
    {"expressionType": "SQL", "sqlExpression": "COUNT(DISTINCT user_pseudo_id)", "label": "Users"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"},
    {"expressionType": "SQL", "sqlExpression": "AVG(total_engagement_time_msec / 1000)", "label": "Avg Engagement (sec)"},
    {"expressionType": "SQL", "sqlExpression": "COUNTIF(session_pageviews = 1) / NULLIF(COUNT(*), 0) * 100", "label": "Bounce Rate (%)"}
  ],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "source IS NOT NULL"
  }],
  "row_limit": 30,
  "order_desc": true
}
```

### チャネル × 地域（テーブル、ID 308）
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": ["source", "geo_region"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"}
  ],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "source IS NOT NULL AND geo_country = 'Japan' AND geo_region IS NOT NULL"
  }],
  "row_limit": 50,
  "order_desc": true
}
```

### チャネル × 時間帯（折れ線、ID 309）
```json
{
  "viz_type": "echarts_timeseries_line",
  "datasource": "28__table",
  "x_axis": "session_hour",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  }],
  "groupby": ["source"],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "source IN ('googleads.g.doubleclick.net', 'google', 'newsdig.tbs.co.jp', 'investor-a.com', 'rekisiru.com')"
  }],
  "y_axis_format": ",d",
  "show_legend": true,
  "x_axis_sort_asc": true
}
```

### チャネル × 新規/リピーター構成（積み上げ棒、ID 310）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "source",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  }],
  "groupby": ["new_vs_returning"],
  "stack": "Stack",
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "source IS NOT NULL AND new_vs_returning IS NOT NULL"
  }],
  "row_limit": 10,
  "y_axis_format": ",d",
  "show_legend": true
}
```

### チャネル × 新規/リピーター詳細（テーブル、ID 311）
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": ["source", "medium", "new_vs_returning"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"},
    {"expressionType": "SQL", "sqlExpression": "COUNT(DISTINCT user_pseudo_id)", "label": "Users"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"},
    {"expressionType": "SQL", "sqlExpression": "AVG(total_engagement_time_msec / 1000)", "label": "Avg Engagement (sec)"}
  ],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "source IS NOT NULL AND new_vs_returning IS NOT NULL"
  }],
  "row_limit": 30,
  "order_desc": true
}
```

### チャネル × 曜日（テーブル、ID 312）
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": ["source", "day_of_week"],
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  }],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "source IS NOT NULL AND day_of_week IS NOT NULL"
  }],
  "row_limit": 50,
  "order_desc": true
}
```

### Chart 268: 広告効率分析（Cost vs CV）
```json
{
  "viz_type": "bubble",
  "datasource": "27__table",
  "entity": "event_date",
  "x": {
    "expressionType": "SQL",
    "sqlExpression": "SUM(ads_cost)",
    "label": "Cost"
  },
  "y": {
    "expressionType": "SQL",
    "sqlExpression": "SUM(conversions)",
    "label": "Conversions"
  },
  "size": {
    "expressionType": "SQL",
    "sqlExpression": "SUM(ads_clicks)",
    "label": "Clicks"
  },
  "max_bubble_size": 25
}
```

### Chart 269: 週別広告費推移
```json
{
  "viz_type": "echarts_timeseries_line",
  "datasource": "27__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1W",
  "metrics": [
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(ads_cost)",
      "label": "Cost"
    }
  ],
  "y_axis_format": "¥,.0f"
}
```

### Chart 270: パフォーマンスサマリー（30日）
```json
{
  "viz_type": "table",
  "datasource": "27__table",
  "query_mode": "aggregate",
  "groupby": [],
  "metrics": [
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(ads_cost)",
      "label": "Cost"
    },
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(ads_clicks)",
      "label": "Clicks"
    },
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(ads_impressions)",
      "label": "Impressions"
    },
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(conversions)",
      "label": "Conversions"
    },
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(revenue)",
      "label": "Revenue"
    },
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(ads_cost) / NULLIF(SUM(ads_clicks), 0)",
      "label": "CPC"
    },
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(ads_clicks) / NULLIF(SUM(ads_impressions), 0) * 100",
      "label": "CTR (%)"
    },
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(revenue) / NULLIF(SUM(ads_cost), 0)",
      "label": "ROAS"
    },
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(ads_cost) / NULLIF(SUM(conversions), 0)",
      "label": "CPA"
    }
  ],
  "adhoc_filters": [
    {
      "clause": "WHERE",
      "expressionType": "SQL",
      "sqlExpression": "event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)"
    }
  ],
  "row_limit": 1
}
```

### Chart 328: KPI BigNumber（全期間）
```json
{
  "viz_type": "big_number",
  "datasource": "27__table",
  "metric": {
    "expressionType": "SQL",
    "sqlExpression": "SUM(revenue) / NULLIF(SUM(ads_cost), 0)",
    "label": "ROAS"
  },
  "show_trend_line": false,
  "y_axis_format": ".2f"
}
```

### Chart 321: コスト vs CTR 散布図（バブル）
```json
{
  "viz_type": "bubble",
  "datasource": "27__table",
  "entity": "event_date",
  "x": {
    "expressionType": "SQL",
    "sqlExpression": "ROUND(SUM(ads_cost) / NULLIF(SUM(ads_clicks), 0), 2)",
    "label": "CPC (円)"
  },
  "y": {
    "expressionType": "SQL",
    "sqlExpression": "ROUND(SUM(ads_clicks) / NULLIF(SUM(ads_impressions), 0) * 100, 2)",
    "label": "CTR (%)"
  },
  "size": {
    "expressionType": "SQL",
    "sqlExpression": "SUM(ads_cost)",
    "label": "Cost"
  },
  "max_bubble_size": 35,
  "adhoc_filters": [
    {
      "clause": "WHERE",
      "subject": "event_date",
      "operator": "TEMPORAL_RANGE",
      "comparator": "Last 60 days",
      "expressionType": "SIMPLE"
    }
  ],
  "x_axis_format": ",.2f",
  "y_axis_format": ",.2f"
}
```

### Chart 322: 日別広告パフォーマンス詳細テーブル
```json
{
  "viz_type": "table",
  "datasource": "27__table",
  "query_mode": "aggregate",
  "groupby": ["event_date"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "SUM(ads_cost)", "label": "Cost"},
    {"expressionType": "SQL", "sqlExpression": "SUM(ads_clicks)", "label": "Clicks"},
    {"expressionType": "SQL", "sqlExpression": "SUM(ads_impressions)", "label": "Impressions"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"},
    {"expressionType": "SQL", "sqlExpression": "SUM(revenue)", "label": "Revenue"},
    {"expressionType": "SQL", "sqlExpression": "SUM(ads_cost) / NULLIF(SUM(ads_clicks), 0)", "label": "CPC"},
    {"expressionType": "SQL", "sqlExpression": "SUM(ads_clicks) / NULLIF(SUM(ads_impressions), 0) * 100", "label": "CTR (%)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions) / NULLIF(SUM(ads_clicks), 0) * 100", "label": "CVR (%)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(revenue) / NULLIF(SUM(ads_cost), 0)", "label": "ROAS"}
  ],
  "orderby": [["Cost", false]],
  "row_limit": 60,
  "adhoc_filters": [
    {
      "clause": "WHERE",
      "subject": "event_date",
      "operator": "TEMPORAL_RANGE",
      "comparator": "Last 90 days",
      "expressionType": "SIMPLE"
    }
  ]
}
```

### Chart 323: 日別広告費×CV×ROAS（複合）
```json
{
  "viz_type": "mixed_timeseries",
  "datasource": "27__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1D",
  "metrics": [
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(ads_cost)",
      "label": "Cost"
    }
  ],
  "seriesType": "bar",
  "metrics_b": [
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"},
    {"expressionType": "SQL", "sqlExpression": "SUM(revenue) / NULLIF(SUM(ads_cost), 0)", "label": "ROAS"}
  ],
  "secondarySeriesType": "line",
  "y_axis_format": ",.0f",
  "y_axis_format_secondary": ".2f",
  "adhoc_filters": [
    {
      "clause": "WHERE",
      "subject": "event_date",
      "operator": "TEMPORAL_RANGE",
      "comparator": "Last 60 days",
      "expressionType": "SIMPLE"
    }
  ],
  "adhoc_filters_b": [
    {
      "clause": "WHERE",
      "subject": "event_date",
      "operator": "TEMPORAL_RANGE",
      "comparator": "Last 60 days",
      "expressionType": "SIMPLE"
    }
  ]
}
```

### Chart 324: CPC推移（90日）
```json
{
  "viz_type": "echarts_timeseries_line",
  "datasource": "27__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1D",
  "metrics": [
    {
      "expressionType": "SQL",
      "sqlExpression": "SUM(ads_cost) / NULLIF(SUM(ads_clicks), 0)",
      "label": "CPC (円)"
    }
  ],
  "adhoc_filters": [
    {
      "clause": "WHERE",
      "subject": "event_date",
      "operator": "TEMPORAL_RANGE",
      "comparator": "Last 90 days",
      "expressionType": "SIMPLE"
    }
  ],
  "y_axis_format": ",.2f",
  "show_legend": true,
  "rich_tooltip": true
}
```
