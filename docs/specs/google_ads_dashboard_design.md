# Google Ads パフォーマンスダッシュボード設計書

## 概要
Google Ads の広告パフォーマンスを包括的に分析するダッシュボード。
コスト、クリック、コンバージョン、ROAS、CPAなどの主要指標を可視化し、広告効率を最適化する。

## データソース

### BigQueryビュー: v_ga_ads_performance

**既存ビュー**を活用（新規作成不要）

#### スキーマ
- `event_date` (DATE) - 日付（Temporal列）
- `sessions` (INTEGER) - セッション数
- `users` (INTEGER) - ユーザー数
- `revenue` (FLOAT) - 収益
- `conversions` (INTEGER) - コンバージョン数
- `ads_cost` (FLOAT) - 広告費
- `ads_clicks` (INTEGER) - クリック数
- `ads_impressions` (INTEGER) - インプレッション数
- `roas` (FLOAT) - ROAS（Return on Ad Spend）
- `cac` (FLOAT) - CAC（Customer Acquisition Cost）

#### データ規模
- **期間**: 2025-08-07 ～ 2025-10-09（約2ヶ月）
- **レコード数**: 231行（日別集計）
- **総広告費**: ¥15,474.47
- **総クリック数**: 775
- **総インプレッション**: 26,424
- **総コンバージョン**: 0（期間中CVなし）
- **CTR**: 約2.93%
- **CPC**: 約¥20/クリック

## Superset実装

### データセット

**Dataset 27**: `v_ga_ads_performance`
- **Database**: BigQuery GA Data (ID: 2)
- **Schema**: analytics_456071139
- **Main Temporal Column**: event_date

### ダッシュボード構成

**Dashboard 19**: 「Google Ads パフォーマンス」

#### セクション1: KPI サマリー（BigNumbers）

**Row 1: KPI BigNumbers（実装版: 8個）**

**期間比較あり（10月 vs 9月）**:
- Chart 258: 広告費
- Chart 259: クリック数
- Chart 260: インプレッション数
- Chart 261: コンバージョン数
- Chart 263: CPC（クリック単価）
- Chart 272: CVR（コンバージョン率）

**全期間データ（比較なし）**:
- Chart 262: ROAS（広告費対効果）
- Chart 271: CPA（獲得単価）

**注**: 10月のコンバージョンがゼロのため、ROASとCPAは全期間データで表示

##### Chart 258: 広告費（10月 vs 9月）
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
  "y_axis_format": "¥,.0f"
}
```

##### Chart 259: クリック数（10月 vs 9月）
- `metric`: `SUM(ads_clicks)`
- `y_axis_format`: `,d`
- フィルター: 2025-10-01 ～ 2025-10-31

##### Chart 260: インプレッション（10月 vs 9月）
- `metric`: `SUM(ads_impressions)`
- `y_axis_format`: `,d`
- フィルター: 2025-10-01 ～ 2025-10-31

##### Chart 261: コンバージョン数（10月 vs 9月）
- `metric`: `SUM(conversions)`
- `y_axis_format`: `,d`
- フィルター: 2025-10-01 ～ 2025-10-31

##### Chart 262: ROAS（全期間）
- `metric`: `SUM(revenue) / NULLIF(SUM(ads_cost), 0)`
- `y_axis_format`: `.2f`
- **フィルター**: なし（全期間データ）
- **理由**: 10月のCVがゼロのため期間限定不可
- **解釈**: ROAS > 1.0 なら広告費に対して収益が上回る

##### Chart 263: CPC（10月 vs 9月）
- `metric`: `SUM(ads_cost) / NULLIF(SUM(ads_clicks), 0)`
- `y_axis_format`: `¥,.2f`
- **解釈**: 1クリックあたりのコスト（低いほど良い）
- **注**: CPAではなくCPCに変更（CVゼロのため）

##### Chart 271: CPA（全期間）
- `metric`: `SUM(ads_cost) / NULLIF(SUM(conversions), 0)`
- `y_axis_format`: `¥,.2f`
- **フィルター**: なし（全期間データ）
- **解釈**: 1コンバージョンあたりの獲得コスト

##### Chart 272: CVR（10月 vs 9月）
- `metric`: `SUM(conversions) / NULLIF(SUM(ads_clicks), 0) * 100`
- `y_axis_format`: `.2f`
- **解釈**: クリックからのコンバージョン率（%）

#### セクション2: トレンド分析

**Row 2: 日別広告指標**

##### Chart 264: 日別広告指標（コスト・クリック）
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
  }]
}
```

##### Chart 265: 日別CV・ROAS推移
- Query A: `SUM(conversions)`
- Query B: `SUM(revenue) / NULLIF(SUM(ads_cost), 0)`
- 2軸チャート

**Row 3: CTR・週別トレンド**

##### Chart 266: CTR推移
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

##### Chart 269: 週別広告費推移
- `time_grain_sqla`: `P1W`（週次集計）
- `metric`: `SUM(ads_cost)`

#### セクション3: 効率分析

**Row 4: 広告効率可視化**

##### Chart 268: 広告効率分析（Cost vs CV）
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

**Row 5: サマリーテーブル**

##### Chart 267: 月別パフォーマンステーブル
- `adhoc_columns`: `FORMAT_DATE('%Y-%m', event_date)` で月別集計
- 全主要指標を表示（Cost, Clicks, Impressions, CVs, CTR, CPC, ROAS, CPA）

##### Chart 270: パフォーマンスサマリー（30日）
- 直近30日の全指標を1行で表示
- クイックサマリー用

#### セクション4: 指標詳細分析（追加 2025-11-12）

より詳細な指標間の相関を把握し、異常値の早期発見に役立つ3チャートを追加した。

##### Chart 321: コスト vs CTR 散布図（バブル）
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
  "adhoc_filters": [{
    "clause": "WHERE",
    "subject": "event_date",
    "operator": "TEMPORAL_RANGE",
    "comparator": "Last 60 days",
    "expressionType": "SIMPLE"
  }],
  "x_axis_format": ",.2f",
  "y_axis_format": ",.2f"
}
```
- X軸/Y軸のラベルに `(円)` / `(%)` を付け、表示値は2桁小数まで丸めて視認性を向上

##### Chart 322: 日別広告パフォーマンス詳細テーブル
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
  "adhoc_filters": [{
    "clause": "WHERE",
    "subject": "event_date",
    "operator": "TEMPORAL_RANGE",
    "comparator": "Last 90 days",
    "expressionType": "SIMPLE"
  }]
}
```
- 直近90日を日別に並べ、主要指標を一括確認
- コスト降順で並べることで、集中監視すべき日が一目でわかる

##### Chart 323: 日別広告費×CV×ROAS（複合）
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
  "seriesType": "bar",
  "metrics_b": [
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"},
    {"expressionType": "SQL", "sqlExpression": "SUM(revenue) / NULLIF(SUM(ads_cost), 0)", "label": "ROAS"}
  ],
  "secondarySeriesType": "line",
  "y_axis_format": ",.0f",
  "y_axis_format_secondary": ".2f",
  "adhoc_filters": [{
    "clause": "WHERE",
    "subject": "event_date",
    "operator": "TEMPORAL_RANGE",
    "comparator": "Last 60 days",
    "expressionType": "SIMPLE"
  }],
  "adhoc_filters_b": [{
    "clause": "WHERE",
    "subject": "event_date",
    "operator": "TEMPORAL_RANGE",
    "comparator": "Last 60 days",
    "expressionType": "SIMPLE"
  }]
}
```
- コスト（棒）とコンバージョン・ROAS（折れ線）を同時に監視
- コスト増減と成果指標の連動性を確認

##### Chart 324: CPC推移（90日）
```json
{
  "viz_type": "echarts_timeseries_line",
  "datasource": "27__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1D",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "SUM(ads_cost) / NULLIF(SUM(ads_clicks), 0)",
    "label": "CPC (円)"
  }],
  "adhoc_filters": [{
    "clause": "WHERE",
    "subject": "event_date",
    "operator": "TEMPORAL_RANGE",
    "comparator": "Last 90 days",
    "expressionType": "SIMPLE"
  }],
  "y_axis_format": ",.2f",
  "show_legend": true,
  "rich_tooltip": true
}
```
- 直近90日のクリック単価推移を可視化（Y軸は数値フォーマットのみ、凡例/ラベルに「(円)」を付与して通貨表示を明示）

**作成手順（API再現のポイント）**
1. Explore で同等のチャートを作成し、DevTools Network から `chart/` リクエストの `Request Payload` を取得
2. 上記テンプレート（`params`/`query_context`）を JSON として組み立て、`/api/v1/chart/` に POST
3. CSRFトークン（`/api/v1/security/csrf_token/`）と `session` Cookie または `Authorization: Bearer <token>` を付与
4. ダッシュボードに追加後、Row 4 の下に新しい行を作り、横並び（Chart 321 & 322）＋ 下段に Chart 323 と Chart 324 を配置

---

## 主要指標の定義

### 基本指標
- **Cost（広告費）**: `SUM(ads_cost)`
- **Clicks（クリック数）**: `SUM(ads_clicks)`
- **Impressions（インプレッション数）**: `SUM(ads_impressions)`
- **Conversions（CV数）**: `SUM(conversions)`
- **Revenue（収益）**: `SUM(revenue)`

### 効率指標
- **CTR（Click Through Rate）**: `SUM(ads_clicks) / NULLIF(SUM(ads_impressions), 0) * 100`
  - クリック率（%）
  - 高いほど広告が魅力的
- **CPC（Cost Per Click）**: `SUM(ads_cost) / NULLIF(SUM(ads_clicks), 0)`
  - 1クリックあたりのコスト
  - 低いほど効率的
- **ROAS（Return on Ad Spend）**: `SUM(revenue) / NULLIF(SUM(ads_cost), 0)`
  - 広告費に対する収益の倍率
  - ROAS > 1.0 で黒字
- **CPA（Cost Per Acquisition）**: `SUM(ads_cost) / NULLIF(SUM(conversions), 0)`
  - 1CVあたりの獲得コスト
  - 低いほど効率的

### CVR（Conversion Rate）
- `SUM(conversions) / NULLIF(SUM(ads_clicks), 0) * 100`
- クリックからのCV率（%）

## 推奨レイアウト

```
┌────────────────────────────────────────────────────────┐
│ Row 1: KPI BigNumbers                                  │
│ [Cost][Clicks][Impr][CVs][ROAS][CPA]                   │
├────────────────────────┬───────────────────────────────┤
│ Row 2:                 │                               │
│ Chart 264              │ Chart 265                     │
│ 日別広告指標           │ 日別CV・ROAS                  │
│ (コスト・クリック)     │                               │
├────────────────────────┼───────────────────────────────┤
│ Row 3:                 │                               │
│ Chart 266              │ Chart 269                     │
│ CTR推移                │ 週別広告費                    │
├────────────────────────┴───────────────────────────────┤
│ Row 4:                                                 │
│ Chart 268: 広告効率分析（Bubble: Cost vs CV）         │
├────────────────────────┬───────────────────────────────┤
│ Row 5:                 │                               │
│ Chart 267              │ Chart 270                     │
│ 月別パフォーマンス     │ サマリー（30日）              │
└────────────────────────┴───────────────────────────────┘
```

## 分析の使い方

### 日次モニタリング
1. **Row 1のKPI BigNumbers**で今月の状況を一目で確認
2. 先月比を見て改善/悪化を把握

### トレンド分析
1. **Chart 264（日別広告指標）**: コストとクリックの日次推移を確認
2. **Chart 265（日別CV・ROAS）**: 収益性の日次変動を把握
3. **Chart 266（CTR推移）**: 広告クリエイティブの効果を追跡

### 効率改善
1. **Chart 268（Bubble）**: コストとCVの関係を可視化
   - バブルサイズ（クリック数）が大きいのに低CVの日を特定
   - 改善が必要な期間を発見
2. **Chart 267（月別テーブル）**: 月ごとのパフォーマンス比較

### 意思決定
- **ROAS < 1.0**: 広告費が収益を上回っている → 入札調整・クリエイティブ改善
- **CPA が高い**: 獲得効率が悪い → ターゲティング見直し
- **CTR が低い**: 広告が魅力的でない → クリエイティブ改善
- **CVR が低い**: LPや導線に問題 → LP改善・ターゲット見直し

## 注意点

### データの特徴
- 現在のデータは**日別集計**のみ
- キャンペーン別、広告グループ別の詳細は含まれていない
- より詳細な分析が必要な場合は、ビューを拡張

### データ期間
- 2025-08-07 ～ 2025-10-09（約2ヶ月）
- MTD（今月）の比較は10月データまで

### データ期間の注意
- **実装版**: 2025-11-10現在、最新データは2025-10-09まで
- **BigNumbers**: 10月（2025-10-01 ～ 2025-10-31）vs 9月の比較
- **CV/収益データ**: 期間中ゼロのため、ROAS/CPAは全期間データで表示
- **通貨**: 全ての金額を円（¥）で表示

## トラブルシューティング

### 「No results」エラー（MTD BigNumbers）
- **原因**: 今月のデータが存在しない
- **対処**: フィルターを「Last month」に変更してテスト

### 「ROAS/CPA が null」
- **原因**: 分母がゼロ（コストまたはCV数がゼロ）
- **対処**: `NULLIF`を使用して0除算を回避（実装済み）

### 「CTR が異常に高い/低い」
- **原因**: インプレッション数の記録漏れ
- **確認**: `ads_impressions`の値を検証

## 拡張案

### Phase 2（オプション）
1. **キャンペーン別分析**: ビューにキャンペーン情報を追加
2. **デバイス別分析**: モバイル/デスクトップ別の効率比較
3. **時間帯別分析**: 時間別のパフォーマンス
4. **予算管理**: 月次予算との比較、消化率追跡
5. **アラート設定**: CPAやROASの閾値監視

### ビュー拡張の方向性
現在の`v_ga_ads_performance`は日別の全体集計のみ。
より詳細な分析には以下の拡張が有効：

```sql
-- キャンペーン別に拡張する場合
CREATE OR REPLACE VIEW v_ga_ads_campaign_performance AS
SELECT 
  event_date,
  (SELECT value.string_value FROM UNNEST(event_params) WHERE key='campaign') AS campaign,
  COUNT(DISTINCT user_pseudo_id) AS users,
  -- ... その他の集計
FROM events_*
WHERE gclid IS NOT NULL -- 広告経由のみ
GROUP BY event_date, campaign
```

