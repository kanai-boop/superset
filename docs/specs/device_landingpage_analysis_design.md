# デバイス・ランディングページ分析設計書

## 概要
ユーザーのデバイスタイプ（モバイル、タブレット、デスクトップ）とランディングページ別のパフォーマンスを分析。
デバイス最適化とLP改善のための洞察を提供する。

## データソース

### BigQueryビュー: v_ga_sessions

**既存ビュー**を活用（新規作成不要）

#### 分析に使用する列
- `device_category` (STRING) - デバイス種類（mobile, tablet, desktop, smart tv）
- `landing_page` (STRING) - ランディングページURL
- `session_pageviews` (INTEGER) - セッション内PV数
- `total_engagement_time_msec` (INTEGER) - エンゲージメント時間（ミリ秒）
- `conversions` (INTEGER) - コンバージョン数
- `user_pseudo_id` (STRING) - ユーザーID

## データの特徴（全期間: 2025-08-02 ～ 2025-11-10）

### デバイス構成
- **Mobile**: 10,218セッション（83.5%）
  - 直帰率: 81.3%
  - 平均エンゲージメント: 9.8秒
- **Tablet**: 1,303セッション（10.7%）
  - 直帰率: 77.4%
  - 平均エンゲージメント: 4.5秒
- **Desktop**: 708セッション（5.8%）
  - 直帰率: 79.2%
  - 平均エンゲージメント: 22.2秒（最も高い）
- **Smart TV**: 4セッション（0.03%）

### ランディングページ
- **ユニーク数**: 10,076種類
- **TOP LP**: https://winglish.site/（97.8%のセッション）
- **その他主要LP**:
  - /01_word: 92セッション（直帰率75.0%、エンゲージ46.8秒）
  - /02_svocm: 48セッション（直帰率81.2%）
  - /03_reading: 26セッション

## Superset実装

### データセット

**Dataset 28**: `v_ga_sessions`（既存）
- すべての分析で同じデータセットを使用
- 追加のメトリクス定義は不要（アドホックメトリクスを使用）

### ダッシュボード構成

**Dashboard 20**: 「デバイス・ランディングページ分析」

## セクション1: デバイス分析

### Chart 273: デバイス別セッション数
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
  "groupby": [],
  "orientation": "horizontal",
  "row_limit": 10,
  "y_axis_format": ",d"
}
```

### Chart 274: デバイス別直帰率
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "device_category",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNTIF(session_pageviews = 1) / NULLIF(COUNT(*), 0) * 100",
    "label": "Bounce Rate (%)"
  }],
  "orientation": "horizontal",
  "y_axis_format": ".1f"
}
```

**直帰率の定義**: セッション内で1ページだけ見て離脱した割合
- 計算式: `COUNTIF(session_pageviews = 1) / COUNT(*) * 100`
- 低いほど良い（ユーザーが複数ページを閲覧）

### Chart 275: デバイス別平均エンゲージメント時間
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "device_category",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "AVG(total_engagement_time_msec / 1000)",
    "label": "Avg Engagement (sec)"
  }],
  "orientation": "horizontal",
  "y_axis_format": ".1f"
}
```

**エンゲージメント時間**: ユーザーがアクティブにページを操作していた時間
- 長いほど良い（コンテンツへの関心が高い）
- Desktopが最も高い（22.2秒）

### Chart 276: デバイス別セッション推移（月別）
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
  "groupby": ["device_category"],
  "stack": "Stack",
  "show_legend": true
}
```

**積み上げ棒グラフ**: デバイス別の構成比の変化を時系列で追跡

## セクション2: ランディングページ分析

### Chart 277: LP別セッション数 TOP10
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "base_landing_page",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  }],
  "orientation": "horizontal",
  "row_limit": 10,
  "y_axis_format": ",d"
}
```

**URLパラメータ除外**: `v_ga_sessions`ビューに`base_landing_page`列を追加（`REGEXP_EXTRACT(landing_page, r'^[^?]+')`）

**重要**: `adhoc_columns`ではなく、ビュー側で`base_landing_page`列を定義することで確実に動作

### Chart 278: LP別直帰率 TOP10
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "base_landing_page",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNTIF(session_pageviews = 1) / NULLIF(COUNT(*), 0) * 100",
    "label": "Bounce Rate (%)"
  }],
  "orientation": "horizontal",
  "row_limit": 10,
  "y_axis_format": ".1f"
}
```

### Chart 279: LP別パフォーマンステーブル TOP20
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": ["base_landing_page"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"},
    {"expressionType": "SQL", "sqlExpression": "COUNT(DISTINCT user_pseudo_id)", "label": "Users"},
    {"expressionType": "SQL", "sqlExpression": "SUM(session_pageviews)", "label": "Pageviews"},
    {"expressionType": "SQL", "sqlExpression": "COUNTIF(session_pageviews = 1) / NULLIF(COUNT(*), 0) * 100", "label": "Bounce Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "AVG(total_engagement_time_msec / 1000)", "label": "Avg Engagement (sec)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"}
  ],
  "row_limit": 20,
  "order_desc": true
}
```

**全主要指標を一覧表示**: Sessions, Users, Pageviews, Bounce Rate, Engagement, Conversions

**重要変更**: `adhoc_columns`ではなく`groupby`に`base_landing_page`を直接指定

### Chart 280: LP別エンゲージメント分析（Bubble）
```json
{
  "viz_type": "bubble",
  "datasource": "28__table",
  "entity": "base_landing_page",
  "x": {
    "expressionType": "SQL",
    "sqlExpression": "AVG(total_engagement_time_msec / 1000)",
    "label": "Avg Engagement (sec)"
  },
  "y": {
    "expressionType": "SQL",
    "sqlExpression": "COUNTIF(session_pageviews = 1) / NULLIF(COUNT(*), 0) * 100",
    "label": "Bounce Rate (%)"
  },
  "size": {
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  },
  "max_bubble_size": 25,
  "row_limit": 50
}
```

**重要変更**: `entity`を`base_landing_page`に変更

**散布図での可視化**: 
- X軸: エンゲージメント時間（高い = 良い）
- Y軸: 直帰率（低い = 良い）
- サイズ: セッション数
- **理想的なLP**: 右下（高エンゲージメント、低直帰率）

## 主要指標の定義

### デバイス分析指標
- **Sessions**: `COUNT(*)`
- **Users**: `COUNT(DISTINCT user_pseudo_id)`
- **Bounce Rate**: `COUNTIF(session_pageviews = 1) / COUNT(*) * 100`
- **Avg Engagement Time**: `AVG(total_engagement_time_msec / 1000)` (秒)

### ランディングページ指標
- **Sessions by LP**: `COUNT(*)` GROUP BY `landing_page`
- **Bounce Rate by LP**: 直帰セッション率
- **Avg Engagement by LP**: LP別の平均滞在時間
- **Conversions by LP**: LP別のCV数

### 直帰（Bounce）の定義
セッション内のページビュー数が1の場合に直帰とみなす:
```sql
COUNTIF(session_pageviews = 1)
```

## 分析の使い方

### デバイス最適化
1. **Chart 273（セッション数）**: どのデバイスが多いか確認
   - Mobile中心のトラフィック → モバイルファーストで最適化
2. **Chart 275（エンゲージメント）**: デバイス別の満足度
   - Desktopが高い → コンテンツ品質は良好
   - Tabletが低い → タブレット表示の改善が必要
3. **Chart 274（直帰率）**: デバイス別の問題発見
   - 高直帰率のデバイス → UX改善の優先度

### LP改善
1. **Chart 277（セッション数）**: トラフィックの多いLPを特定
2. **Chart 278（直帰率）**: 改善が必要なLPを発見
   - 高直帰率 → ファーストビューやコンテンツの見直し
3. **Chart 280（Bubble）**: 理想的なLPのパターン発見
   - 右下エリア（低直帰、高エンゲージ）のLPを参考に
4. **Chart 279（テーブル）**: 詳細データで優先順位付け

## データから見えた洞察

### デバイス特性
- **Mobile優勢**: 全体の83.5%がモバイル
- **Desktopの質**: セッション数は少ないが、エンゲージメントは2倍以上（22.2秒 vs 9.8秒）
- **Tabletの課題**: エンゲージメントが最も低い（4.5秒）→ UI改善の余地

### ランディングページ集中
- **TOPページ一極集中**: 97.8%がTOPページから流入
- **サブページ**: /01_word（単語学習）が2位だが、わずか92セッション
- **直帰率**: 全体的に高い（75-84%）→ コンテンツ導線の改善が必要

### 改善提案
1. **モバイル体験の向上**: 最大セグメントなので優先的に最適化
2. **Tabletの見直し**: 低エンゲージメントの原因調査
3. **LP多様化**: TOPページ以外への流入経路を増やす
4. **直帰率改善**: 関連コンテンツへの導線、CTAの最適化

## 推奨レイアウト

```
┌────────────────────────────────────────────────────────┐
│ セクション1: デバイス分析                              │
├────────────────┬─────────────────┬──────────────────────┤
│ Chart 273      │ Chart 274       │ Chart 275            │
│ セッション数   │ 直帰率          │ エンゲージメント時間 │
├────────────────┴─────────────────┴──────────────────────┤
│ Chart 276: デバイス別推移（月別、積み上げ）           │
├────────────────────────────────────────────────────────┤
│ セクション2: ランディングページ分析                    │
├────────────────────────┬───────────────────────────────┤
│ Chart 277              │ Chart 278                     │
│ LP別セッション TOP10   │ LP別直帰率 TOP10              │
├────────────────────────┴───────────────────────────────┤
│ Chart 279: LP別パフォーマンステーブル TOP20           │
├────────────────────────────────────────────────────────┤
│ Chart 280: LP別エンゲージメント分析（Bubble）         │
└────────────────────────────────────────────────────────┘
```

## トラブルシューティング

### LP別チャートでURLが長すぎて見づらい
- **対処**: `adhoc_columns`で`REGEXP_EXTRACT`を使いURLパラメータを除外
- **実装済み**: 全LPチャートで対応済み

### デバイス別で"(not set)"が表示される
- **原因**: `device_category`がNULLのセッション
- **対処**: `WHERE device_category IS NOT NULL`フィルターを追加

### 直帰率が100%のページがある
- **原因**: すべてのセッションが1PVのみ
- **確認**: セッション数が少ない（サンプル不足）可能性

### エンゲージメント時間が0秒
- **原因**: ユーザーが即離脱、またはバックグラウンド状態
- **正常**: 広告リダイレクトページなどで発生

## 拡張案

### Phase 2（オプション）
1. **デバイス × チャネル**: デバイス別のチャネルパフォーマンス
2. **LP × デバイス**: LPごとのデバイス構成比
3. **時系列分析**: デバイス別の日次・週次トレンド
4. **地域 × デバイス**: 地域別のデバイス利用傾向
5. **新規 vs リピーター × デバイス**: デバイス別のユーザー属性

## 活用例

### モバイルファースト戦略
- Mobileが83.5%を占める → モバイル最適化が最優先
- Desktop比でエンゲージメントが低い → モバイルUX改善の余地

### コンテンツ導線改善
- 直帰率が高い（77-81%）→ 関連記事・次のアクションへの導線強化
- /01_wordはエンゲージ46.8秒と高い → このパターンを他ページに適用

### A/Bテスト優先度
- TOPページが97.8% → ここの改善が最大インパクト
- /01_wordなどのサブページ → 高エンゲージメントだが流入少ない → SEO強化

