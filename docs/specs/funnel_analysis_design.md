# コンバージョンファネル分析設計書

## 概要
ユーザーのCV到達までの行動ステップを分析。
各ステップの通過率・離脱率を可視化し、ボトルネックを特定してCV率を改善する。

## データソース

### BigQueryビュー: v_ga_funnel_analysis

**新規作成ビュー**

#### スキーマ
```sql
CREATE OR REPLACE VIEW `v_ga_funnel_analysis` AS
SELECT
  event_date,
  unique_session_id,
  user_pseudo_id,
  device_category,
  source,
  medium,
  geo_region,
  new_vs_returning,
  -- Funnel Steps (0 or 1)
  1 AS step_1_landing,
  CASE WHEN session_pageviews >= 2 THEN 1 ELSE 0 END AS step_2_engaged,
  CASE WHEN total_engagement_time_msec >= 10000 THEN 1 ELSE 0 END AS step_3_browse,
  CASE WHEN session_pageviews >= 3 THEN 1 ELSE 0 END AS step_4_action,
  CASE WHEN conversions >= 1 THEN 1 ELSE 0 END AS step_5_conversion
FROM v_ga_sessions
```

#### ファネルステップ定義

**Step 1: ランディング**
- 定義: 全セッション
- 条件: `1`（常に1）

**Step 2: エンゲージ**
- 定義: 直帰しなかった
- 条件: `session_pageviews >= 2`

**Step 3: 閲覧継続**
- 定義: 10秒以上滞在
- 条件: `total_engagement_time_msec >= 10000`

**Step 4: アクション**
- 定義: 3ページ以上閲覧
- 条件: `session_pageviews >= 3`

**Step 5: コンバージョン**
- 定義: CVイベント発生
- 条件: `conversions >= 1`

## データの特徴（全期間: 2025-08-02 ～ 2025-11-10）

### 全体ファネル

| ステップ | 数 | 通過率 | 前ステップからの離脱率 |
|---------|-----|--------|---------------------|
| **Step 1: ランディング** | 14,355 | 100.0% | - |
| **Step 2: エンゲージ** | 4,399 | 30.6% | **69.4%** ⚠️ |
| **Step 3: 閲覧継続** | 2,275 | 15.8% | 48.3% |
| **Step 4: アクション** | 2,802 | 19.5% | -23.2% |
| **Step 5: CV** | 12,145 | **84.6%** | -333.4% ✨ |

**最大の課題**: Step 1→2 の離脱率69.4%（直帰）

**ポジティブ**: 最終CV率84.6%と非常に高い

### デバイス別ファネル

| デバイス | Landing | Engage Rate | CVR |
|---------|---------|-------------|-----|
| **Mobile** | 11,949 | 30.0% | **85.0%** |
| **Tablet** | 1,461 | 30.5% | **88.8%** ← 最高 |
| **Desktop** | 941 | **39.0%** ← 最高 | 72.6% |

**洞察**:
- Desktopの方がエンゲージ率が高い（39.0%）
- しかしCV率はMobile/Tabletの方が高い（85-89%）
- Desktopユーザーは探索型、Mobile/Tabletは目的型

### チャネル別ファネル効率

| チャネル | Landing | Engage Rate | CVR |
|---------|---------|-------------|-----|
| **Google Ads** | 3,210 | **16.0%** ⚠️ | **91.5%** ✨ |
| **Google Organic** | 233 | **43.3%** ✨ | 41.6% |
| newsdig.tbs.co.jp | 221 | 13.6% | 93.2% |
| investor-a.com | 125 | 20.0% | 99.2% |

**洞察**:
- **Google Ads**: エンゲージ率低い（16.0%）だがCV率高い（91.5%）
  - 質より量、CV直結型
- **Google Organic**: エンゲージ率高い（43.3%）だがCV率低い（41.6%）
  - 探索型、教育型コンテンツ

## Superset実装

### データセット

**Dataset 38**: `v_ga_funnel_analysis`（新規作成）

### ダッシュボード構成

**Dashboard 26**: 「コンバージョンファネル分析」

### チャート一覧

#### Chart 313: ~~コンバージョンファネル（全体）~~ 削除

**注意**: Superset API経由でのFunnelチャート作成が "Not enough segments" エラーにより失敗するため、このチャートは削除されました。Chart 314-318で代替分析が可能です。

#### Chart 314: ファネルステップ詳細
```json
{
  "viz_type": "table",
  "datasource": "38__table",
  "query_mode": "raw",
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "SUM(step_1_landing)", "label": "Step1: Landing"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_2_engaged)", "label": "Step2: Engaged"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_3_browse)", "label": "Step3: Browse"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_4_action)", "label": "Step4: Action"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_5_conversion)", "label": "Step5: CV"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_2_engaged) / NULLIF(SUM(step_1_landing), 0) * 100", "label": "Engage Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_5_conversion) / NULLIF(SUM(step_1_landing), 0) * 100", "label": "CVR (%)"}
  ]
}
```

#### Chart 315: デバイス別ファネル比較
```json
{
  "viz_type": "table",
  "datasource": "38__table",
  "query_mode": "aggregate",
  "groupby": ["device_category"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "SUM(step_1_landing)", "label": "Landing"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_2_engaged)", "label": "Engaged"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_5_conversion)", "label": "CV"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_2_engaged) / NULLIF(SUM(step_1_landing), 0) * 100", "label": "Engage Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_5_conversion) / NULLIF(SUM(step_1_landing), 0) * 100", "label": "CVR (%)"}
  ]
}
```

#### Chart 316: チャネル別ファネル効率 TOP20
```json
{
  "viz_type": "table",
  "datasource": "38__table",
  "query_mode": "aggregate",
  "groupby": ["source", "medium"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "SUM(step_1_landing)", "label": "Landing"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_2_engaged)", "label": "Engaged"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_5_conversion)", "label": "CV"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_2_engaged) / NULLIF(SUM(step_1_landing), 0) * 100", "label": "Engage Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_5_conversion) / NULLIF(SUM(step_1_landing), 0) * 100", "label": "CVR (%)"}
  ],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "source IS NOT NULL"
  }],
  "row_limit": 20
}
```

#### Chart 317: 新規 vs リピーター ファネル比較
```json
{
  "viz_type": "table",
  "datasource": "38__table",
  "query_mode": "aggregate",
  "groupby": ["new_vs_returning"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "SUM(step_1_landing)", "label": "Landing"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_2_engaged)", "label": "Engaged"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_3_browse)", "label": "Browse"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_4_action)", "label": "Action"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_5_conversion)", "label": "CV"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_2_engaged) / NULLIF(SUM(step_1_landing), 0) * 100", "label": "Engage Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(step_5_conversion) / NULLIF(SUM(step_1_landing), 0) * 100", "label": "CVR (%)"}
  ],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "new_vs_returning IS NOT NULL"
  }]
}
```

#### Chart 318: デバイス別離脱率
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "38__table",
  "x_axis": "device_category",
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "(1 - SUM(step_2_engaged) / NULLIF(SUM(step_1_landing), 0)) * 100", "label": "Step1→2 離脱率"},
    {"expressionType": "SQL", "sqlExpression": "(1 - SUM(step_3_browse) / NULLIF(SUM(step_2_engaged), 0)) * 100", "label": "Step2→3 離脱率"}
  ],
  "orientation": "horizontal",
  "y_axis_format": ".1f",
  "show_legend": true
}
```

## CV最適化戦略

### 優先度1: 直帰率改善（最重要）

**現状**: 69.4%が直帰（Step 1→2）

**施策**:
1. **ランディングページ最適化**:
   - ファーストビューの改善
   - CTAボタンの明確化
   - 価値提案の強化
2. **ページ速度向上**:
   - 画像最適化
   - JavaScriptの遅延読み込み
   - CDN活用
3. **コンテンツの関連性**:
   - 広告メッセージとLPの一致
   - ユーザー意図に合ったコンテンツ
4. **モバイルUX改善**:
   - タップしやすいボタン
   - スクロール不要で要点表示

**目標**: 直帰率を55%に削減（14.4pt改善）

### 優先度2: チャネル別最適化

**Google Ads（エンゲージ低、CV高）**:
- **現状**: エンゲージ16.0%、CVR 91.5%
- **特徴**: CV直結型
- **施策**:
  - LP簡潔化（すぐCVできる）
  - フォーム最適化
  - 明確なCTA
- **目標**: エンゲージ率向上不要、CV数最大化

**Google Organic（エンゲージ高、CV低）**:
- **現状**: エンゲージ43.3%、CVR 41.6%
- **特徴**: 探索型
- **施策**:
  - コンテンツ内のCTA追加
  - リードマグネット（無料資料など）
  - リターゲティング広告
- **目標**: CVR を60%に向上（18.4pt改善）

### 優先度3: デバイス別最適化

**Mobile/Tablet（CV率高い）**:
- **現状**: CVR 85-89%
- **施策**: 現状維持、トラフィック増加に注力

**Desktop（エンゲージ高、CV低）**:
- **現状**: エンゲージ39.0%、CVR 72.6%
- **施策**:
  - 詳細コンテンツ内にCTA
  - デモ動画
  - チャットボット

## 洞察と戦略

### 発見1: 直帰率が最大のボトルネック
- **現象**: 69.4%が直帰
- **解釈**: ランディングページが魅力的でない
- **施策**: LP最適化が最優先

### 発見2: エンゲージしたユーザーは高CV
- **現象**: 最終CV率84.6%
- **解釈**: エンゲージさえすればCVしやすい
- **施策**: エンゲージさせることに注力

### 発見3: Google Adsは質より量
- **現象**: エンゲージ16.0%、CVR 91.5%
- **解釈**: 目的意識が明確なユーザー
- **施策**: 量を増やす（予算増額）

### 発見4: Organicはエンゲージ重視
- **現象**: エンゲージ43.3%、CVR 41.6%
- **解釈**: 情報収集段階
- **施策**: ナーチャリング（育成）

### 発見5: Mobile/TabletがCV効率高い
- **現象**: CVR 85-89%
- **解釈**: モバイルユーザーが主要顧客
- **施策**: モバイルファースト戦略

## 推奨レイアウト

```
┌────────────────────────────────────────────────────────────┐
│ Row 1:                                                     │
│ Chart 316: チャネル別ファネル効率 TOP20（全幅）           │
├────────────────────────┬───────────────────────────────────┤
│ Row 2:                 │                                   │
│ Chart 315              │ Chart 317                         │
│ デバイス別ファネル     │ 新規vsリピーターファネル         │
├────────────────────────┼───────────────────────────────────┤
│ Row 3:                 │                                   │
│ Chart 318              │ Chart 314                         │
│ デバイス別離脱率       │ ファネル詳細                      │
└────────────────────────┴───────────────────────────────────┘
```

**注意**: Chart 313は技術的問題により削除されました。Chart 314-318で十分なファネル分析が可能です。

## 実践的なアクションプラン

### 短期（1週間以内）
1. **ヒートマップ導入**: ランディングページの改善点特定
2. **ページ速度測定**: PageSpeed Insights実行
3. **A/Bテスト準備**: LP2パターン作成

### 中期（1ヶ月以内）
1. **LP改善実施**:
   - ファーストビュー変更
   - CTA最適化
   - 速度改善
2. **A/Bテスト実施**: 2週間テスト
3. **効果測定**: 直帰率の変化確認

### 長期（3ヶ月以内）
1. **チャネル別LP作成**:
   - Google Ads向け: CV直結型
   - Organic向け: 教育型
2. **デバイス別最適化**:
   - Mobile: 簡潔化
   - Desktop: 詳細化
3. **継続的改善**: 週次でファネル監視

## トラブルシューティング

### CV率が異常に高い（84.6%）
- **原因**: CVイベント定義が緩い可能性
- **確認**: `conversion_event_page_view`の定義確認
- **対処**: CVイベント定義の見直し

### ステップ定義が適切でない
- **原因**: PV数や時間の閾値が不適切
- **対処**: 閾値を調整（現在: PV>=2, 10秒, PV>=3）
- **改善**: ビジネスに合わせてカスタマイズ

### ファネルが逆流している（Step 4→5）
- **原因**: CVがStep 2で発生する可能性
- **解釈**: 問題なし、ステップをスキップしてCVする

## 拡張案

### Phase 2（オプション）
1. **地域別ファネル**: 地域ごとのファネル効率
2. **時間帯別ファネル**: 時間帯ごとのCV率
3. **コンテンツ別ファネル**: ページ別のファネル効率
4. **カスタムイベントファネル**: 特定アクション（クリック、スクロール）を含む
5. **コホート別ファネル**: 初回訪問月別のファネル変化


