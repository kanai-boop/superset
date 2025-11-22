# マスターダッシュボード設計書（Executive Overview）

## 概要
経営層・マネージャー向けの総合ダッシュボード。
全ての重要指標を一画面で確認でき、他の専門ダッシュボードへのナビゲーションハブとして機能する。

## 目的
- **朝イチで見るダッシュボード**: 毎朝最初にチェックする画面
- **全体像の把握**: ビジネスの健康状態を即座に判断
- **深掘りへの入り口**: 詳細分析ダッシュボードへの導線

## データソース

### Dataset 28: v_ga_sessions
既存のセッションビューを使用。全ての主要指標が含まれている。

### Dataset 27: v_ga_ads_performance
Google Ads費用データ用。

## ダッシュボード構成

### Dashboard 27（新規作成）: 「マスターダッシュボード（Executive Overview）」

## チャート一覧

### Row 1: 主要KPI BigNumbers（6つ、10月 vs 9月比較）

#### Chart 319: セッション数（10月）
```json
{
  "viz_type": "big_number",
  "datasource": "28__table",
  "metric": {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"},
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "event_date >= '2025-10-01' AND event_date < '2025-11-01'"
  }],
  "y_axis_format": ",d",
  "compare_lag": 1,
  "comparison_type": "percentage",
  "show_delta": true,
  "show_percentage": true
}
```

#### Chart 320: 新規ユーザー数（10月）
```json
{
  "viz_type": "big_number",
  "datasource": "28__table",
  "metric": {"expressionType": "SQL", "sqlExpression": "COUNTIF(new_vs_returning = 'new')", "label": "New Users"},
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "event_date >= '2025-10-01' AND event_date < '2025-11-01'"
  }],
  "y_axis_format": ",d",
  "compare_lag": 1,
  "comparison_type": "percentage",
  "show_delta": true,
  "show_percentage": true
}
```

#### Chart 321: エンゲージメント率（10月、%）
```json
{
  "viz_type": "big_number",
  "datasource": "28__table",
  "metric": {"expressionType": "SQL", "sqlExpression": "COUNTIF(is_engaged_session = 1) / NULLIF(COUNT(*), 0) * 100", "label": "Engagement Rate"},
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "event_date >= '2025-10-01' AND event_date < '2025-11-01'"
  }],
  "y_axis_format": ".1f",
  "compare_lag": 1,
  "comparison_type": "percentage",
  "show_delta": true,
  "show_percentage": true
}
```

#### Chart 322: 平均エンゲージメント時間（10月、秒）
```json
{
  "viz_type": "big_number",
  "datasource": "28__table",
  "metric": {"expressionType": "SQL", "sqlExpression": "AVG(total_engagement_time_msec) / 1000", "label": "Avg Engagement Time (sec)"},
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "event_date >= '2025-10-01' AND event_date < '2025-11-01'"
  }],
  "y_axis_format": ".1f",
  "compare_lag": 1,
  "comparison_type": "percentage",
  "show_delta": true,
  "show_percentage": true
}
```

#### Chart 323: コンバージョン数（10月）
```json
{
  "viz_type": "big_number",
  "datasource": "28__table",
  "metric": {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"},
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "event_date >= '2025-10-01' AND event_date < '2025-11-01'"
  }],
  "y_axis_format": ",d",
  "compare_lag": 1,
  "comparison_type": "percentage",
  "show_delta": true,
  "show_percentage": true
}
```

#### Chart 324: CVR（10月、%）
```json
{
  "viz_type": "big_number",
  "datasource": "28__table",
  "metric": {"expressionType": "SQL", "sqlExpression": "SUM(conversions) / NULLIF(COUNT(*), 0) * 100", "label": "CVR"},
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "event_date >= '2025-10-01' AND event_date < '2025-11-01'"
  }],
  "y_axis_format": ".1f",
  "compare_lag": 1,
  "comparison_type": "percentage",
  "show_delta": true,
  "show_percentage": true
}
```

### Row 2: トレンドチャート（2つ）

#### Chart 325: セッション・CV推移（直近30日）
```json
{
  "viz_type": "mixed_timeseries",
  "datasource": "28__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1D",
  "metrics": [{"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"}],
  "metrics_b": [{"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"}],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)"
  }],
  "y_axis_format": ",d",
  "y_axis_format_secondary": ",d"
}
```

#### Chart 326: チャネル別セッション構成（10月、積み上げ棒）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1D",
  "metrics": [{"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"}],
  "groupby": ["source"],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "event_date >= '2025-10-01' AND event_date < '2025-11-01'"
  }],
  "stack": "Stack",
  "y_axis_format": ",d",
  "show_legend": true,
  "row_limit": 5
}
```

### Row 3: クイックインサイト（3つ）

#### Chart 327: デバイス構成（10月、円グラフ）
```json
{
  "viz_type": "pie",
  "datasource": "28__table",
  "groupby": ["device_category"],
  "metric": {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"},
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "event_date >= '2025-10-01' AND event_date < '2025-11-01'"
  }],
  "show_legend": true,
  "show_labels": true,
  "label_type": "percent"
}
```

#### Chart 328: 地域 TOP5（10月、テーブル）
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": ["geo_region"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"},
    {"expressionType": "SQL", "sqlExpression": "AVG(total_engagement_time_msec) / 1000", "label": "Avg Engagement (sec)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"}
  ],
  "adhoc_filters": [
    {
      "clause": "WHERE",
      "expressionType": "SQL",
      "sqlExpression": "event_date >= '2025-10-01' AND event_date < '2025-11-01'"
    },
    {
      "clause": "WHERE",
      "expressionType": "SQL",
      "sqlExpression": "geo_region IS NOT NULL"
    }
  ],
  "row_limit": 5
}
```

#### Chart 329: ファネル簡易版（10月、テーブル）
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": [],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Landing"},
    {"expressionType": "SQL", "sqlExpression": "COUNTIF(session_pageviews >= 2)", "label": "Engaged"},
    {"expressionType": "SQL", "sqlExpression": "COUNTIF(conversions >= 1)", "label": "Converted"},
    {"expressionType": "SQL", "sqlExpression": "COUNTIF(session_pageviews >= 2) / NULLIF(COUNT(*), 0) * 100", "label": "Engage Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "COUNTIF(conversions >= 1) / NULLIF(COUNT(*), 0) * 100", "label": "CVR (%)"}
  ],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "event_date >= '2025-10-01' AND event_date < '2025-11-01'"
  }],
  "row_limit": 1
}
```

### Row 4: 月次KPIテーブル（1つ、全幅）

#### Chart 330: 月次KPIサマリー（直近3ヶ月）
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": [],
  "columns": [{"sqlExpression": "FORMAT_DATE('%Y-%m', event_date)", "label": "Month"}],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"},
    {"expressionType": "SQL", "sqlExpression": "COUNTIF(new_vs_returning = 'new')", "label": "New Users"},
    {"expressionType": "SQL", "sqlExpression": "COUNTIF(is_engaged_session = 1) / NULLIF(COUNT(*), 0) * 100", "label": "Engagement Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "AVG(total_engagement_time_msec) / 1000", "label": "Avg Engagement (sec)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions) / NULLIF(COUNT(*), 0) * 100", "label": "CVR (%)"}
  ],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "event_date >= '2025-08-01' AND event_date < '2025-11-01'"
  }],
  "row_limit": 3
}
```

## 推奨レイアウト

```
┌──────────────────────────────────────────────────────────────┐
│ Row 1: KPI BigNumbers（6列）                                │
│ ┌─────────┬─────────┬─────────┬─────────┬─────────┬────────┐│
│ │Chart 319│Chart 320│Chart 321│Chart 322│Chart 323│Chart324││
│ │Sessions │New Users│Engage % │Avg Time │  CVs    │  CVR   ││
│ └─────────┴─────────┴─────────┴─────────┴─────────┴────────┘│
├───────────────────────────────┬──────────────────────────────┤
│ Row 2: トレンド                │                              │
│ Chart 325                     │ Chart 326                    │
│ セッション・CV推移（30日）    │ チャネル別構成（10月）       │
├───────────┬───────────┬───────┴──────────────────────────────┤
│ Row 3:    │           │                                      │
│ Chart 327 │ Chart 328 │ Chart 329                            │
│ デバイス  │ 地域TOP5  │ ファネル簡易版                       │
├───────────┴───────────┴──────────────────────────────────────┤
│ Row 4: 月次KPIテーブル（全幅）                               │
│ Chart 330: 直近3ヶ月のKPI推移                                │
└──────────────────────────────────────────────────────────────┘
```

## 手動作成手順（API制限のため）

### ⚠️ 重要
Superset API経由での新規チャート作成が「Not enough segments」エラーで失敗するため、**UIから手動で作成**してください。

### Step 1: ダッシュボード作成
1. Superset UIにログイン
2. **Dashboards** → **+ Dashboard**
3. タイトル: `マスターダッシュボード（Executive Overview）`
4. **Save**

### Step 2: BigNumber 6種作成
既存のBigNumberチャート（Chart 258など）を**複製**して作成するのが最速です。

#### 方法A: 既存チャートを複製
1. **Chart 258**（広告費BigNumber）を開く
2. 右上 **「...」** → **「Save as」**
3. 新しい名前を入力: `セッション数（10月）`
4. **Data** タブで修正:
   - **Dataset**: `v_ga_sessions (ID: 28)` に変更
   - **Metric**: Custom SQL → `COUNT(*)`
   - **Filters**: `event_date >= '2025-10-01' AND event_date < '2025-11-01'`
5. **Customize** タブ:
   - **Number format**: `,d`
   - **Show comparison**: ✅ ON
   - **Comparison lag**: `1`
6. **Save**
7. Dashboard 27に追加

残り5つも同様に作成（Metric部分のみ変更）:
- **New Users**: `COUNTIF(new_vs_returning = 'new')`
- **Engagement Rate**: `COUNTIF(is_engaged_session = 1) / NULLIF(COUNT(*), 0) * 100` (format: `.1f`)
- **Avg Engagement Time**: `AVG(total_engagement_time_msec) / 1000` (format: `.1f`)
- **Conversions**: `SUM(conversions)` (format: `,d`)
- **CVR**: `SUM(conversions) / NULLIF(COUNT(*), 0) * 100` (format: `.1f`)

#### 方法B: 新規作成
1. Dashboard 27を開く
2. **「+」** → **「Create a new chart」**
3. **Dataset**: `v_ga_sessions (ID: 28)`
4. **Chart Type**: `Big Number`
5. **Data** タブで設定（上記と同じ）
6. **Save** → Dashboard 27に追加

### Step 3: トレンドチャート2種作成
#### Chart 325: セッション・CV推移
1. **Chart Type**: `Mixed Time-Series`
2. **Dataset**: `v_ga_sessions (ID: 28)`
3. **Query A**:
   - **Time Column**: `event_date`
   - **Metric**: `COUNT(*)`（Sessions）
4. **Query B**:
   - **Metric**: `SUM(conversions)`
5. **Filters**: `event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)`

#### Chart 326: チャネル別構成
1. **Chart Type**: `Time-series Bar Chart`
2. **Dataset**: `v_ga_sessions (ID: 28)`
3. **Time Column**: `event_date`
4. **Metric**: `COUNT(*)`
5. **Group by**: `source`
6. **Filters**: `event_date >= '2025-10-01' AND event_date < '2025-11-01'`
7. **Customize** → **Stacking**: `Stack`
8. **Row limit**: `5`

### Step 4: クイックインサイト3種作成
#### Chart 327: デバイス構成
1. **Chart Type**: `Pie Chart`
2. **Dataset**: `v_ga_sessions (ID: 28)`
3. **Dimensions**: `device_category`
4. **Metric**: `COUNT(*)`
5. **Filters**: 10月フィルター

#### Chart 328: 地域TOP5
1. **Chart Type**: `Table`
2. **Dataset**: `v_ga_sessions (ID: 28)`
3. **Group by**: `geo_region`
4. **Metrics**: `COUNT(*)`, `AVG(total_engagement_time_msec) / 1000`, `SUM(conversions)`
5. **Filters**: 10月フィルター + `geo_region IS NOT NULL`
6. **Row limit**: `5`

#### Chart 329: ファネル簡易版
1. **Chart Type**: `Table`
2. **Dataset**: `v_ga_sessions (ID: 28)`
3. **Metrics** (5つのCustom SQL):
   - `COUNT(*)` as "Landing"
   - `COUNTIF(session_pageviews >= 2)` as "Engaged"
   - `COUNTIF(conversions >= 1)` as "Converted"
   - `COUNTIF(session_pageviews >= 2) / NULLIF(COUNT(*), 0) * 100` as "Engage Rate (%)"
   - `COUNTIF(conversions >= 1) / NULLIF(COUNT(*), 0) * 100` as "CVR (%)"
4. **Filters**: 10月フィルター
5. **Row limit**: `1`

### Step 5: 月次KPIテーブル作成
#### Chart 330: 月次KPIサマリー
1. **Chart Type**: `Table`
2. **Dataset**: `v_ga_sessions (ID: 28)`
3. **Columns**: Custom SQL → `FORMAT_DATE('%Y-%m', event_date)` as "Month"
4. **Metrics** (6つのCustom SQL):
   - `COUNT(*)` as "Sessions"
   - `COUNTIF(new_vs_returning = 'new')` as "New Users"
   - `COUNTIF(is_engaged_session = 1) / NULLIF(COUNT(*), 0) * 100` as "Engagement Rate (%)"
   - `AVG(total_engagement_time_msec) / 1000` as "Avg Engagement (sec)"
   - `SUM(conversions)` as "Conversions"
   - `SUM(conversions) / NULLIF(COUNT(*), 0) * 100` as "CVR (%)"
5. **Filters**: `event_date >= '2025-08-01' AND event_date < '2025-11-01'`
6. **Row limit**: `3`

### Step 6: ダッシュボードレイアウト調整
1. Dashboard 27を開く
2. **Edit Dashboard**
3. チャートをドラッグ＆ドロップで配置（上記レイアウト参照）
4. **Save**

## データ洞察（2025年8-10月）

### 全体トレンド
- **セッション数**: 8月3,210 → 9月5,873 → 10月5,272（9月ピーク後やや減少）
- **新規ユーザー**: 8月2,374 → 9月4,371 → 10月3,938（新規率約75%で安定）
- **エンゲージメント率**: 8月32.2% → 9月32.7% → 10月32.0%（横ばい）
- **平均エンゲージ時間**: 8月8.7秒 → 9月8.5秒 → 10月8.8秒（微増）
- **CV数**: 8月3,354 → 9月6,199 → 10月5,625（セッションに連動）
- **CVR**: 8月104.5% → 9月105.6% → 10月106.7%（**異常に高い**）

### 主要課題

#### 1. CVRが100%超え（異常値）
- **現象**: CVRが100%を超えている（8-10月すべて）
- **原因**: 
  - CVイベント定義が緩すぎる（`conversion_event_page_view`など）
  - 1セッションで複数CVがカウントされている
- **対策**: 
  - CVイベント定義の見直し
  - セッションあたりのCV数を`MIN(conversions, 1)`で制限
  - または、ユニークCV数（`COUNTIF(conversions >= 1)`）を使用

#### 2. 直帰率が高い（約70%）
- **現象**: エンゲージメント率32%（直帰率68%）
- **課題**: 7割近くが直帰している
- **対策**: 
  - ランディングページ最適化
  - ファーストビューの改善
  - ページ速度向上

#### 3. 9月ピークの原因不明
- **現象**: 9月にセッション・CV数が大幅増加
- **考察**: 
  - 広告キャンペーン実施？
  - 季節要因（新学期）？
  - 特定イベント？
- **対策**: 広告データと照合して原因特定

### チャネル別洞察（10月）
- **Google Ads**: 最大セッション源（約60%）
- **Organic**: エンゲージメント高い
- **Referral**: CV効率高い

### デバイス別洞察（10月）
- **Mobile**: 83.5%（圧倒的シェア）
- **Desktop**: 高エンゲージ（22.2秒 vs Mobile 6.5秒）
- **Tablet**: 高CVR（88.8%）

### 地域別洞察（10月）
- **東京**: 14.9%（最大）
- **関東圏**: 28%集中
- **上位5地域**: 東京、大阪、神奈川、愛知、埼玉

## 活用方法

### 毎朝のチェックリスト
1. **Row 1（BigNumbers）**: 昨日の主要指標確認
   - 前日比で異常値がないか？
   - トレンドは順調か？
2. **Row 2（トレンド）**: 直近30日の動き
   - 急激な増減がないか？
   - チャネル構成に変化はないか？
3. **Row 3（クイックインサイト）**: セグメント確認
   - デバイス構成は正常か？
   - 地域別で異常はないか？
   - ファネルのボトルネックは？
4. **Row 4（月次KPI）**: 月次推移
   - 月次目標達成ペースか？
   - 前月比で改善しているか？

### 異常検知時のアクション
- **セッション激減**: 広告停止？サイトダウン？
- **CVR急落**: CVイベント設定変更？ページエラー？
- **エンゲージ低下**: コンテンツ品質低下？UX問題？

### 深掘り分析への導線
マスターダッシュボードで異常を発見したら、該当する専門ダッシュボードで詳細分析:
- **Google Ads問題** → Dashboard 19（Google Ads パフォーマンス）
- **デバイス問題** → Dashboard 20（デバイス・LP分析）
- **新規獲得問題** → Dashboard 21（新規 vs リピーター分析）
- **時間帯問題** → Dashboard 22（時間帯・曜日パターン）
- **地域問題** → Dashboard 23（地域別パフォーマンス）
- **コンテンツ問題** → Dashboard 24（コンテンツパフォーマンス）
- **チャネル問題** → Dashboard 25（チャネル × セグメント）
- **ファネル問題** → Dashboard 26（コンバージョンファネル）

## 拡張案

### Phase 2（オプション）
1. **リアルタイムKPI**: 本日の主要指標（BigQueryのリアルタイムエクスポート使用）
2. **アラート機能**: 異常値検知時の通知（Superset Alerts機能）
3. **予測分析**: 月末予測値の表示（機械学習モデル）
4. **目標線**: KPIに目標値ラインを追加
5. **ダッシュボードナビゲーション**: 他ダッシュボードへのリンクボタン

### Phase 3（高度な機能）
1. **カスタマイズ可能**: ユーザーごとに表示KPIを選択
2. **期間比較**: 前年同期比較
3. **セグメント別KPI**: チャネル別・デバイス別KPIを並列表示
4. **スコアカード**: 健康度スコア（0-100点）

## トラブルシューティング

### チャート作成で「Not enough segments」エラー
- **原因**: Superset API経由での新規作成に制限
- **対策**: 既存チャートを複製（Save as）して作成
- **参考**: `troubleshooting.md` の「ファネル分析チャート」セクション

### BigNumberの比較が効かない
- **原因**: `compare_lag`や`comparison_type`の設定ミス
- **対策**: 
  - `compare_lag: 1`（前期間比較）
  - `comparison_type: "percentage"`（パーセント表示）
  - `show_delta: true`, `show_percentage: true`

### 月次KPIテーブルでグループ化エラー
- **原因**: `FORMAT_DATE()`をColumnsではなくGroup byに設定
- **対策**: **Columns**タブで`FORMAT_DATE('%Y-%m', event_date)`をCustom SQL列として追加

### CVRが100%超え
- **原因**: CVイベント定義が緩い、または1セッション複数CV
- **対策**: 
  - メトリクスを`COUNTIF(conversions >= 1) / NULLIF(COUNT(*), 0) * 100`に変更（ユニークCV）
  - CVイベント定義を見直し（BigQuery側）

## まとめ

マスターダッシュボードは**ビジネスの健康診断**です。

- **毎朝5分**: 全体像を把握
- **異常検知**: 問題を早期発見
- **深掘り**: 専門ダッシュボードへ誘導

このダッシュボードを起点に、データドリブンな意思決定を実現します。

