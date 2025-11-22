# ページ経路分析（Path Exploration）設計書

## 概要
GA4の「経路データ探索」機能をSupersetで再現。
ユーザーがどのページから訪問し、どのような経路を辿ってコンバージョンに至ったかを分析する。

## 目的
- **始点分析**: CVに至ったユーザーが最初に訪問したページを特定
- **終点分析**: CVの直前にユーザーが見ていたページを特定
- **遷移分析**: ページ間の移動パターンを可視化
- **経路最適化**: CVに至りやすい導線を発見し、サイト改善に活用

## データモデル設計

### BigQueryビュー: v_ga_page_paths

#### 目的
- コンバージョンに至ったユーザーのページ閲覧履歴を時系列で追跡
- 始点（最初のページ）、終点（最後のページ）、ページ間遷移を集計
- From → To の遷移パターンを抽出

#### SQL実装

```sql
CREATE OR REPLACE VIEW `winglish-gemini-cli.analytics_456071139.v_ga_page_paths` AS
WITH 
conversions AS (
  SELECT 
    user_pseudo_id,
    event_timestamp AS conversion_timestamp,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS conversion_date
  FROM `winglish-gemini-cli.analytics_456071139.events_*`
  WHERE event_name = 'conversion_event_page_view'
    AND _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY))
),

page_sequence AS (
  SELECT 
    e.user_pseudo_id,
    c.conversion_timestamp,
    c.conversion_date,
    e.event_timestamp,
    REGEXP_EXTRACT((SELECT value.string_value FROM UNNEST(e.event_params) WHERE key='page_location'), r'^[^?]+') AS base_url,
    (SELECT value.string_value FROM UNNEST(e.event_params) WHERE key='page_title') AS page_title,
    ROW_NUMBER() OVER (
      PARTITION BY e.user_pseudo_id, c.conversion_timestamp 
      ORDER BY e.event_timestamp
    ) AS page_order,
    COUNT(*) OVER (
      PARTITION BY e.user_pseudo_id, c.conversion_timestamp
    ) AS total_pages
  FROM `winglish-gemini-cli.analytics_456071139.events_*` e
  INNER JOIN conversions c 
    ON e.user_pseudo_id = c.user_pseudo_id
    AND e.event_timestamp < c.conversion_timestamp
  WHERE e.event_name = 'page_view'
    AND e._TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY))
),

page_transitions AS (
  SELECT 
    user_pseudo_id,
    conversion_timestamp,
    conversion_date,
    base_url AS from_page,
    page_title AS from_title,
    LEAD(base_url) OVER (
      PARTITION BY user_pseudo_id, conversion_timestamp 
      ORDER BY page_order
    ) AS to_page,
    LEAD(page_title) OVER (
      PARTITION BY user_pseudo_id, conversion_timestamp 
      ORDER BY page_order
    ) AS to_title,
    page_order AS step_number,
    total_pages
  FROM page_sequence
)

-- 始点ページ
SELECT 
  conversion_date,
  base_url AS page,
  page_title,
  'start' AS position_type,
  CAST(1 AS INT64) AS step_number,
  NULL AS from_page,
  NULL AS to_page,
  COUNT(DISTINCT user_pseudo_id) AS conversions,
  'position' AS data_type
FROM page_sequence
WHERE page_order = 1
GROUP BY conversion_date, base_url, page_title

UNION ALL

-- 終点ページ
SELECT 
  conversion_date,
  base_url AS page,
  page_title,
  'end' AS position_type,
  CAST(total_pages AS INT64) AS step_number,
  NULL AS from_page,
  NULL AS to_page,
  COUNT(DISTINCT user_pseudo_id) AS conversions,
  'position' AS data_type
FROM page_sequence
WHERE page_order = total_pages
GROUP BY conversion_date, base_url, page_title, total_pages

UNION ALL

-- 遷移エッジ
SELECT 
  conversion_date,
  NULL AS page,
  NULL AS page_title,
  'transition' AS position_type,
  CAST(NULL AS INT64) AS step_number,
  from_page,
  to_page,
  COUNT(DISTINCT user_pseudo_id) AS conversions,
  'edge' AS data_type
FROM page_transitions
WHERE to_page IS NOT NULL
GROUP BY conversion_date, from_page, to_page
```

#### 出力スキーマ

**始点・終点データ** (`data_type = 'position'`):
- `conversion_date` (DATE): コンバージョン日
- `page` (STRING): ページURL（パラメータ除外済み）
- `page_title` (STRING): ページタイトル
- `position_type` (STRING): 'start' または 'end'
- `step_number` (INTEGER): ステップ番号
- `conversions` (INTEGER): CV数

**遷移データ** (`data_type = 'edge'`):
- `from_page` (STRING): 遷移元ページ
- `to_page` (STRING): 遷移先ページ
- `conversions` (INTEGER): この遷移を経たCV数

## Superset実装

### データセット作成

**データセット**: `v_ga_page_paths` (ID: 36)
- **主要列**: `conversion_date`, `page`, `page_title`, `position_type`, `from_page`, `to_page`, `data_type`
- **フィルター条件**:
  - 始点分析: `position_type = 'start' AND data_type = 'position'`
  - 終点分析: `position_type = 'end' AND data_type = 'position'`
  - 遷移分析: `data_type = 'edge'`

### チャート構成

#### Chart 254: 始点ページ TOP10
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "36__table",
  "x_axis": "page",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "SUM(conversions)",
    "label": "CVs"
  }],
  "groupby": [],
  "orientation": "horizontal",
  "row_limit": 10,
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "position_type = 'start'"
  }],
  "y_axis_format": ",d",
  "show_legend": false
}
```

#### Chart 255: 終点ページ TOP10
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "36__table",
  "x_axis": "page",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "SUM(conversions)",
    "label": "CVs"
  }],
  "groupby": [],
  "orientation": "horizontal",
  "row_limit": 10,
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "position_type = 'end'"
  }],
  "y_axis_format": ",d",
  "show_legend": false
}
```

#### Chart 256: ページ遷移テーブル
```json
{
  "viz_type": "table",
  "datasource": "36__table",
  "query_mode": "aggregate",
  "groupby": ["from_page", "to_page"],
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "SUM(conversions)",
    "label": "CVs"
  }],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "data_type = 'edge'"
  }],
  "row_limit": 20,
  "order_desc": true
}
```

#### Chart 257: ページ遷移Sunburst
```json
{
  "viz_type": "sunburst_v2",
  "datasource": "36__table",
  "groupby": ["from_page", "to_page"],
  "metric": {
    "expressionType": "SQL",
    "sqlExpression": "SUM(conversions)",
    "label": "CVs"
  },
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "data_type = 'edge'"
  }],
  "row_limit": 50
}
```

### ダッシュボード構成

**Dashboard 18**: 「ページ経路分析（Path Exploration）」

**推奨レイアウト**:
```
Row 1: [Chart 254: 始点ページ TOP10] [Chart 255: 終点ページ TOP10]
Row 2: [Chart 257: ページ遷移Sunburst（全幅）]
Row 3: [Chart 256: ページ遷移テーブル（全幅）]
```

## 実装結果

### データ規模（直近60日）
- **始点ページ**: 83種類のユニークページ（合計6,500 CVs）
- **終点ページ**: 1,843種類のユニークページ（合計9,638 CVs）
- **ページ遷移**: 895パターンの遷移（合計3,761 CVs）

### 主要な発見
- **始点**: ほとんどがTOPページ（`https://winglish.site/`）から流入
- **終点**: TOPページでのCVが多い
- **遷移**: 同一ページ内での再訪問パターンが多数

## GA4との対応

| GA4機能 | Superset実装 | Chart ID |
|---------|-------------|----------|
| 始点（ここからの経路） | 始点ページ TOP10 | 254 |
| 終点（ここまでの経路） | 終点ページ TOP10 | 255 |
| ノード間の遷移 | ページ遷移テーブル | 256 |
| 経路の可視化 | ページ遷移Sunburst | 257 |

## 注意点

### データ量の考慮
- ページビューイベントの追跡は重い処理
- 直近60日に絞ってクエリを実行
- 本番運用時はマテリアライズドビューの検討を推奨

### URLの正規化
- `REGEXP_EXTRACT(page_location, r'^[^?]+')`でURLパラメータを除外
- 同一ページの集約を実現

### コンバージョン定義
- 実装版: `event_name = 'conversion_event_page_view'`
- 必要に応じてCTE `conversions`の条件を変更

### ダッシュボード作成
- `position_json`のAPI経由更新は不安定
- UI上で手動でチャートを配置することを推奨

## トラブルシューティング

### 「始点・終点ページが重複して見える」
- **原因**: 同一URLでも異なる`conversion_date`でグループ化されている
- **対処**: `conversion_date`を除外するか、日付フィルターを追加

### 「遷移データが少ない」
- **原因**: 単一ページでCVするユーザーが多い（遷移なし）
- **確認**: `total_pages`の分布を確認し、マルチページジャーニーの割合をチェック

### 「同一ページへの遷移が多い」
- **原因**: ページリロードや動的コンテンツの再読み込み
- **対処**: `from_page != to_page`のフィルターを追加

## 拡張案

### Phase 2（オプション）
1. **ステップ別分析**: 1→2→3ステップの詳細な経路
2. **カテゴリ別分析**: ページをカテゴリに分類して集計
3. **セグメント別分析**: チャネル別の経路パターン比較
4. **時系列分析**: 月別の経路変化トレンド

