# コンテンツパフォーマンス分析設計書

## 概要
ページ・コンテンツ別のパフォーマンスを詳細分析。
人気コンテンツ、エンゲージメント、CV貢献度、エントリー・エグジットパターンを可視化し、
コンテンツ戦略とSEO優先順位の最適化に活用する。

## データソース

### BigQueryビュー: v_ga_content_performance

**新規作成ビュー**

#### スキーマ
```sql
CREATE OR REPLACE VIEW `v_ga_content_performance` AS
-- page_view イベントから各ページのパフォーマンス指標を集計
```

#### 主要カラム
- `event_date` (DATE) - イベント日付
- `page_title` (STRING) - ページタイトル
- `base_page_url` (STRING) - URLパラメータ除外後のページURL
- `pageviews` (INTEGER) - ページビュー数
- `unique_users` (INTEGER) - ユニークユーザー数
- `sessions` (INTEGER) - セッション数
- `avg_engagement_sec` (FLOAT) - 平均エンゲージメント時間（秒）
- `entrances` (INTEGER) - エントリー数（セッションの最初のページ）
- `exits` (INTEGER) - エグジット数（セッションの最後のページ）
- `exit_rate` (FLOAT) - 離脱率（%）
- `sessions_with_conversion` (INTEGER) - CVがあったセッション数
- `total_conversions` (INTEGER) - 総コンバージョン数
- `session_conversion_rate` (FLOAT) - セッションCVR（%）

#### 計算ロジック

**エントリー・エグジット判定**:
```sql
ROW_NUMBER() OVER (
  PARTITION BY user_pseudo_id, session_id
  ORDER BY event_timestamp ASC
) AS page_order_asc  -- 1 = エントリー

ROW_NUMBER() OVER (
  PARTITION BY user_pseudo_id, session_id
  ORDER BY event_timestamp DESC
) AS page_order_desc  -- 1 = エグジット
```

**CV関連付け**:
```sql
LEFT JOIN session_conversions
  ON pv.user_pseudo_id = sc.user_pseudo_id 
  AND pv.session_id = sc.session_id
```

**離脱率**:
```sql
SAFE_DIVIDE(exits, pageviews) * 100 AS exit_rate
```

**セッションCVR**:
```sql
SAFE_DIVIDE(sessions_with_conversion, sessions) * 100
```

## データの特徴（全期間: 2025-08-02 ～ 2025-11-10）

### 人気コンテンツ TOP5

| 順位 | ページタイトル | PVs | Sessions | CVR | Engagement | Exit Rate |
|------|---------------|-----|----------|-----|------------|-----------|
| 1 | **TOPページ \| Winglish** | 16,382 | 11,947 | **90.8%** | **12.3秒** | 69.6% |
| 2 | 単語帳 ｜ Winglish | 815 | 535 | 85.1% | 0.0秒 | 27.7% |
| 3 | 英文解釈 \| Winglish | 411 | 319 | 82.2% | 0.0秒 | 32.4% |
| 4 | 長文読解 \| Winglish | 274 | 226 | 89.8% | 0.0秒 | 30.1% |
| 5 | Login \| Winglish | 238 | 188 | **98.8%** | 0.0秒 | 23.0% |

### エントリー・エグジット分析

**エントリー（ランディングページ）**:
- TOPページ: 11,905（83.0%）← 圧倒的
- 単語帳: 93（0.6%）
- 英文解釈: 56（0.4%）
- 長文読解: 26（0.2%）

**エグジット（離脱ページ）**:
- TOPページ: 11,629（80.9%）
- 単語帳: 193（1.3%）
- 英文解釈: 108（0.8%）
- 長文読解: 85（0.6%）

### コンテンツ特性

**TOPページの優位性**:
- PVs: 16,382（全体の約90%）
- エンゲージ: 12.3秒（唯一の長時間）
- CVR: 90.8%（非常に高い）
- エントリー: 11,905（大半がここから開始）

**学習コンテンツの課題**:
- 単語帳・英文解釈・長文読解
- エンゲージ: ほぼ0秒（瞬間閲覧）
- 高いCVR（82-90%）だがエンゲージが低い
- エグジット率も比較的高い

## Superset実装

### データセット

**Dataset 37**: `v_ga_content_performance`（新規作成）

### ダッシュボード構成

**Dashboard 24**: 「コンテンツパフォーマンス分析」

### チャート一覧

#### Chart 299: 人気コンテンツランキング TOP15
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
  "y_axis_format": ",d"
}
```

**横棒グラフ**: ページビュー数でランキング

#### Chart 300: エンゲージメント高いコンテンツ TOP15
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
  "y_axis_format": ".1f"
}
```

**フィルター**: PV 50以上に限定（ノイズ除去）

#### Chart 301: コンテンツ別パフォーマンステーブル TOP30
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
  "row_limit": 30
}
```

#### Chart 302: CV貢献度の高いコンテンツ TOP15
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
  "y_axis_format": ",d"
}
```

#### Chart 303: コンテンツパフォーマンス分析（Bubble）
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
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "pageviews >= 30"
  }],
  "max_bubble_size": 25,
  "row_limit": 50
}
```

**散布図**:
- X軸: エンゲージメント（高い = 良い）
- Y軸: CVR（高い = 良い）
- サイズ: PV数
- **理想ゾーン**: 右上（高エンゲージ、高CVR）

#### Chart 304: 月別コンテンツトレンド（TOP5）
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
  "show_legend": true
}
```

#### Chart 305: エントリー・エグジット分析 TOP20
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
  "row_limit": 20
}
```

## コンテンツ戦略活用方法

### 優先順位付け

**Tier 1: TOPページ最適化（最優先）**
- **現状**: 16,382 PV、CVR 90.8%、エンゲージ12.3秒
- **機会**: さらに改善でCV数増加
- **施策**:
  - ファーストビューの最適化
  - CTAボタンの改善
  - A/Bテスト実施
  - ローディング速度改善

**Tier 2: 学習コンテンツのエンゲージ改善**
- **現状**: エンゲージ0秒（瞬間離脱）
- **課題**: コンテンツが薄い、体験が悪い
- **施策**:
  - コンテンツ充実化
  - インタラクティブ要素追加
  - 学習進捗の可視化
  - 滞在時間向上施策

**Tier 3: エグジット対策**
- **現状**: 単語帳・英文解釈で高いエグジット
- **課題**: 次のアクションが不明確
- **施策**:
  - CTA追加（次の学習へ）
  - 関連コンテンツ提案
  - 学習ガイド表示

### SEO優先順位

**最優先ページ（投資対効果高い）**:
1. **TOPページ**: 既に強いが、さらに強化
   - メタタグ最適化
   - 構造化データ追加
   - コンテンツ拡充
2. **単語帳**: 2番目のトラフィック
   - SEOタイトル改善
   - コンテンツ拡充
3. **英文解釈・長文読解**: 専門性アピール
   - ロングテールキーワード対策

### コンテンツ改善施策

**TOPページ改善（短期）**:
- [ ] ファーストビューのCTA改善
- [ ] ローディング速度測定・改善
- [ ] ヒートマップ分析
- [ ] A/Bテスト（CTA文言、配置）

**学習コンテンツ改善（中期）**:
- [ ] 単語帳のインタラクション追加
- [ ] 英文解釈の解説詳細化
- [ ] 学習進捗の可視化機能
- [ ] 次のステップの明示

**エグジット対策（短期）**:
- [ ] 各ページにCTA追加
- [ ] 「次に学ぶ」レコメンド機能
- [ ] Exit Intent Popup（離脱防止）

## 洞察と戦略

### 発見1: TOPページの圧倒的重要性
- **現象**: 全PVの90%、エントリーの83%
- **解釈**: TOPページがビジネスの要
- **施策**: TOPページへの投資が最大のROI

### 発見2: 学習コンテンツのエンゲージ課題
- **現象**: エンゲージ0秒（瞬間閲覧）
- **解釈**: コンテンツが浅い、または体験が悪い
- **施策**: コンテンツ充実化、インタラクティブ化

### 発見3: 高いCVR（全体的）
- **現象**: 全ページでCVR 80%以上
- **解釈**: CVイベント定義が緩い可能性
- **確認**: CVイベント定義の見直し

### 発見4: Login後の高CVR（98.8%）
- **現象**: Login後はほぼ全員がCV
- **解釈**: ログインユーザーの行動がCVとして計測
- **施策**: ログイン促進施策

## 推奨レイアウト

```
┌────────────────────────┬───────────────────────────────┐
│ Row 1:                 │                               │
│ Chart 299              │ Chart 300                     │
│ 人気ランキング         │ エンゲージ高い                │
├────────────────────────┼───────────────────────────────┤
│ Row 2:                 │                               │
│ Chart 302              │ Chart 304                     │
│ CV貢献度               │ 月別トレンド                  │
├────────────────────────┴───────────────────────────────┤
│ Row 3:                                                 │
│ Chart 301: パフォーマンステーブル TOP30                │
├────────────────────────┬───────────────────────────────┤
│ Row 4:                 │                               │
│ Chart 303              │ Chart 305                     │
│ パフォーマンスBubble   │ エントリーエグジット          │
└────────────────────────┴───────────────────────────────┘
```

## コンテンツ監視指標（KPI）

### 毎週チェック
1. **TOPページ指標**:
   - PV数の推移
   - CVRの変動
   - エンゲージメント時間
2. **新規コンテンツ**:
   - 公開後の初動PV
   - エンゲージメント

### 毎月チェック
1. **コンテンツ全体**:
   - TOP10の入れ替わり
   - エンゲージメント変化
   - CVR変化
2. **エグジット分析**:
   - 高エグジットページの特定
   - 改善施策の効果測定

## トラブルシューティング

### エンゲージメント時間が0秒
- **原因**: GA4のengagement_time_msecが記録されていない
- **確認**: イベントパラメータの設定確認
- **代替**: セッション時間やスクロール深度を使用

### CVRが異常に高い（90%以上）
- **原因**: CVイベント定義が緩い可能性
- **確認**: `conversion_event_page_view`の定義確認
- **対処**: CVイベント定義の見直し

### ページタイトルが重複
- **原因**: 同じタイトルで異なるURL
- **対処**: `base_page_url`でグルーピング
- **改善**: ページタイトルの一意性を確保

## 拡張案

### Phase 2（オプション）
1. **コンテンツカテゴリ分析**: ページをカテゴリ分類して分析
2. **コンテンツ読了率**: スクロール深度から読了率推定
3. **コンテンツ × チャネル**: 流入元別のコンテンツパフォーマンス
4. **コンテンツ × デバイス**: デバイス別のコンテンツ閲覧傾向
5. **コンテンツジャーニー分析**: コンテンツ間の遷移パターン

