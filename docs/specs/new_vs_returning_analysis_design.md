# 新規 vs リピーターユーザー分析設計書

## 概要
新規ユーザーとリピーターユーザーの行動・パフォーマンスを比較分析。
ユーザー獲得施策とリテンション施策の最適化に活用する。

## データソース

### BigQueryビュー: v_ga_sessions

**既存ビュー**を活用（新規作成不要）

#### 使用する列
- `new_vs_returning` (STRING) - "New User" または "Returning User"
- `event_date` (DATE) - セッション日
- `user_pseudo_id` (STRING) - ユーザーID
- `session_pageviews` (INTEGER) - セッション内PV数
- `total_engagement_time_msec` (INTEGER) - エンゲージメント時間
- `conversions` (INTEGER) - コンバージョン数
- `device_category` (STRING) - デバイス種類

## データの特徴（全期間: 2025-08-02 ～ 2025-11-10）

### 構成比
- **新規ユーザー**: 10,754セッション（74.7%）
  - ユーザー数: 9,113
  - 直帰率: 71.6%
  - 平均エンゲージメント: 9.1秒
  - CV数: 11,231
  - CVR: 104.4%

- **リピーター**: 3,601セッション（25.3%）
  - ユーザー数: 1,060
  - 直帰率: 60.9%（新規より10.7pt低い）
  - 平均エンゲージメント: 6.5秒（短いが効率的）
  - CV数: 4,440
  - CVR: 123.3%（新規より18.9pt高い）

### 重要な洞察

**リピーターの特徴**:
- ✅ **直帰率が低い**（60.9% vs 71.6%）→ サイト内回遊が活発
- ⚠️ **エンゲージメントが短い**（6.5秒 vs 9.1秒）→ 目的が明確で効率的
- ✅ **CV率が高い**（123.3% vs 104.4%）→ ロイヤリティ効果

**マーケティング示唆**:
1. **新規獲得が主体**（74.7%）→ 新規向けコンテンツ・導線の最適化が重要
2. **リピーターは高効率**（CVR 123.3%）→ リテンション施策のROIが高い
3. **新規の直帰率改善余地**（71.6%）→ ファーストビュー、LPの改善

## Superset実装

### データセット

**Dataset 28**: `v_ga_sessions`（既存）
- `new_vs_returning`列を活用

### ダッシュボード構成

**Dashboard 21**: 「新規 vs リピーターユーザー分析」

### チャート一覧

#### Chart 281: 新規 vs リピーター構成比
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

**円グラフ**: 新規 vs リピーターの割合を一目で把握

#### Chart 282: 新規 vs リピーター比較テーブル
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

**全主要指標を並べて比較**: 新規とリピーターの違いを一目で把握

#### Chart 283: 月別推移（新規 vs リピーター）
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

**積み上げ棒グラフ**: 月ごとの新規/リピーター比率の変化を追跡

#### Chart 284: デバイス別の新規/リピーター構成
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

**デバイス × ユーザータイプ**: デバイスごとの新規/リピーター比率

#### Chart 285: エンゲージメント比較
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

**横棒グラフ**: エンゲージメント時間の比較

#### Chart 286: 直帰率比較
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

**横棒グラフ**: 直帰率の比較（低い方が良い）

## 主要指標の定義

### 基本指標
- **Sessions**: `COUNT(*)`
- **Users**: `COUNT(DISTINCT user_pseudo_id)`
- **Pageviews**: `SUM(session_pageviews)`
- **PV/Session**: `AVG(session_pageviews)`

### 行動指標
- **Bounce Rate**: `COUNTIF(session_pageviews = 1) / COUNT(*) * 100`
- **Avg Engagement**: `AVG(total_engagement_time_msec / 1000)` (秒)

### CV指標
- **Conversions**: `SUM(conversions)`
- **CVR**: `SUM(conversions) / COUNT(*) * 100`

## 分析の使い方

### 戦略立案
1. **Chart 281（構成比）**: 新規獲得 vs リテンションのバランス確認
   - 新規が多すぎる → リテンション強化
   - リピーターが少ない → ロイヤリティ施策
   
2. **Chart 282（比較テーブル）**: 行動の違いを数値で把握
   - CVRの差 → リピーター向けオファーの効果測定
   - 直帰率の差 → 新規向けコンテンツの課題発見

### 施策評価
3. **Chart 283（月別推移）**: 施策効果の時系列追跡
   - 新規獲得キャンペーン → 新規セッション増加を確認
   - リテンション施策 → リピーターセッション増加を確認

4. **Chart 284（デバイス別構成）**: デバイス × ユーザータイプの最適化
   - Mobileは新規が多い → モバイル新規向けUI
   - Desktopはリピーターが多い → Desktop向け高度機能

### 改善施策
5. **Chart 286（直帰率比較）**: 新規の高直帰率を改善
   - 新規: 71.6% → ファーストビュー改善
   - リピーター: 60.9% → より良好

6. **Chart 285（エンゲージメント）**: エンゲージメント最適化
   - リピーターは短くても効率的 → OK
   - 新規は9.1秒 → さらに引き上げる余地

## マーケティング戦略への示唆

### 新規獲得施策（74.7%が新規）
- **優先度**: 高
- **施策**: 
  - ファーストビューの最適化
  - 明確なバリュープロポジション
  - 次のアクションへの誘導強化
- **KPI**: 新規直帰率を71.6% → 60%台へ

### リテンション施策（CVR 123.3%）
- **優先度**: 高（ROIが高い）
- **施策**:
  - メールマーケティング
  - プッシュ通知
  - パーソナライゼーション
- **KPI**: リピーターセッション数を25.3% → 35%へ

### セグメント別最適化
- **新規 × Mobile**: 最大セグメント → モバイル新規向けLPを最優先
- **リピーター × Desktop**: 高エンゲージ → 高度機能・詳細コンテンツ提供

## 推奨レイアウト

```
┌────────────────────────┬───────────────────────────────┐
│ Row 1:                 │                               │
│ Chart 281              │ Chart 282                     │
│ 構成比（円グラフ）     │ 比較テーブル                  │
├────────────────────────┼───────────────────────────────┤
│ Row 2:                 │                               │
│ Chart 283              │ Chart 284                     │
│ 月別推移               │ デバイス別構成                │
├────────────────────────┼───────────────────────────────┤
│ Row 3:                 │                               │
│ Chart 285              │ Chart 286                     │
│ エンゲージメント比較   │ 直帰率比較                    │
└────────────────────────┴───────────────────────────────┘
```

## 拡張案

### Phase 2（オプション）
1. **チャネル別の新規/リピーター**: どのチャネルが新規獲得に強いか
2. **リピート率分析**: 初回訪問後の再訪率
3. **LTV（Life Time Value）**: ユーザーあたりの累積価値
4. **リピート頻度分析**: 2回目、3回目、4回目以降の行動変化
5. **コホート分析**: 初回訪問月別のリテンション率

## トラブルシューティング

### CVRが100%を超える
- **原因**: 1セッションで複数CVが発生
- **正常**: `conversion_event_page_view`が複数回発生するため
- **対処**: 必要に応じて`COUNT(DISTINCT conversion)`に変更

### 「New User」と「Returning User」以外の値
- **原因**: `new_vs_returning`列がNULL
- **対処**: `WHERE new_vs_returning IS NOT NULL`フィルター追加

### リピーターが少なすぎる
- **原因**: データ期間が短い、またはユーザー定義の問題
- **確認**: `session_number`分布を確認

