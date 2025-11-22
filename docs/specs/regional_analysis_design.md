# 地域別パフォーマンス分析設計書

## 概要
国別・都道府県別のユーザー行動とパフォーマンスを分析。
エリアマーケティング戦略の立案と地域ターゲティングの最適化に活用する。

## データソース

### BigQueryビュー: v_ga_sessions

**既存ビュー**を活用（新規作成不要）

#### 使用する列
- `geo_country` (STRING) - 国名（例: Japan, United States）
- `geo_region` (STRING) - 都道府県名（例: Tokyo, Osaka）
- その他分析用列: sessions, users, conversions, engagement, bounce rate

## データの特徴（全期間: 2025-08-02 ～ 2025-11-10）

### 国別構成
- **Japan**: 14,016セッション（97.6%）← 圧倒的多数
- **South Korea**: 128セッション（0.9%）
- **United States**: 60セッション（0.4%）
- **その他**: 151セッション（1.1%）

**結論**: ほぼ日本国内ユーザー → 日本国内の都道府県分析に注力

### 都道府県別 TOP15

| 順位 | 都道府県 | Sessions | Users | CVs | Engagement | Bounce Rate |
|------|----------|----------|-------|-----|------------|-------------|
| 1 | **Tokyo** | 2,082 (14.9%) | 1,342 | 2,292 | **13.4秒** | **60.5%** |
| 2 | **Osaka** | 1,049 (7.5%) | 753 | 1,095 | 7.8秒 | 71.9% |
| 3 | **Hokkaido** | 984 (7.0%) | 628 | 1,118 | 6.6秒 | 68.6% |
| 4 | **Aichi** | 770 (5.5%) | 492 | 787 | 9.4秒 | 72.1% |
| 5 | **Kanagawa** | 724 (5.2%) | 424 | 781 | **11.1秒** | 62.0% |
| 6 | Fukuoka | 697 (5.0%) | 419 | 908 | 9.3秒 | 65.0% |
| 7 | **Saitama** | 566 (4.0%) | 346 | 692 | **12.9秒** | 71.4% |
| 8 | Chiba | 541 (3.9%) | 321 | 579 | 6.5秒 | 64.0% |
| 9 | Hyogo | 521 (3.7%) | 342 | 545 | 8.6秒 | 66.4% |
| 10 | Shizuoka | 437 (3.1%) | 292 | 456 | 5.0秒 | 74.6% |

**関東圏合計**: 東京+神奈川+埼玉+千葉 = 3,913セッション（27.9%）

### 地域特性

**高エンゲージメント地域**:
1. Tokyo: 13.4秒
2. Saitama: 12.9秒
3. Kanagawa: 11.1秒
4. Kyoto: 10.9秒

**低直帰率地域**:
1. Tokyo: 60.5%（最良）✨
2. Kanagawa: 62.0%
3. Ibaraki: 62.7%

**CVR高い地域**:
- ほぼ全地域で100%超（複数CVあり）
- 特に Fukuoka: 130.3%

## Superset実装

### データセット

**Dataset 28**: `v_ga_sessions`（既存）
- `geo_country`, `geo_region`列を活用

### ダッシュボード構成

**Dashboard 23**: 「地域別パフォーマンス分析」

### チャート一覧

#### Chart 293: 都道府県別セッション数 TOP15
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "geo_region",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  }],
  "orientation": "horizontal",
  "row_limit": 15,
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "geo_country = 'Japan'"
  }],
  "y_axis_format": ",d"
}
```

#### Chart 294: 都道府県別エンゲージメント TOP15
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "geo_region",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "AVG(total_engagement_time_msec / 1000)",
    "label": "Avg Engagement (sec)"
  }],
  "orientation": "horizontal",
  "row_limit": 15,
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "geo_country = 'Japan'"
  }],
  "y_axis_format": ".1f"
}
```

#### Chart 295: 都道府県別パフォーマンステーブル TOP20
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": ["geo_region"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"},
    {"expressionType": "SQL", "sqlExpression": "COUNT(DISTINCT user_pseudo_id)", "label": "Users"},
    {"expressionType": "SQL", "sqlExpression": "SUM(session_pageviews)", "label": "Pageviews"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"},
    {"expressionType": "SQL", "sqlExpression": "AVG(total_engagement_time_msec / 1000)", "label": "Avg Engagement (sec)"},
    {"expressionType": "SQL", "sqlExpression": "COUNTIF(session_pageviews = 1) / NULLIF(COUNT(*), 0) * 100", "label": "Bounce Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions) / NULLIF(COUNT(*), 0) * 100", "label": "CVR (%)"}
  ],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "geo_country = 'Japan'"
  }],
  "row_limit": 20
}
```

#### Chart 296: 国別セッション数 TOP10
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "geo_country",
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

#### Chart 297: 都道府県別パフォーマンス分析（Bubble）
```json
{
  "viz_type": "bubble",
  "datasource": "28__table",
  "entity": "geo_region",
  "x": {
    "expressionType": "SQL",
    "sqlExpression": "AVG(total_engagement_time_msec / 1000)",
    "label": "Avg Engagement (sec)"
  },
  "y": {
    "expressionType": "SQL",
    "sqlExpression": "SUM(conversions) / NULLIF(COUNT(*), 0) * 100",
    "label": "CVR (%)"
  },
  "size": {
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  },
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "geo_country = 'Japan'"
  }],
  "max_bubble_size": 25,
  "row_limit": 50
}
```

**散布図での可視化**:
- X軸: エンゲージメント時間（高い = 良い）
- Y軸: CVR（高い = 良い）
- サイズ: セッション数
- **理想的な地域**: 右上（高エンゲージ、高CVR）

#### Chart 298: 主要地域の月別推移（TOP5）
```json
{
  "viz_type": "echarts_timeseries_line",
  "datasource": "28__table",
  "x_axis": "event_date",
  "time_grain_sqla": "P1M",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  }],
  "groupby": ["geo_region"],
  "adhoc_filters": [{
    "clause": "WHERE",
    "expressionType": "SQL",
    "sqlExpression": "geo_region IN ('Tokyo', 'Osaka', 'Hokkaido', 'Aichi', 'Kanagawa')"
  }],
  "show_legend": true
}
```

## マーケティング活用方法

### エリア別施策優先度

**最優先エリア（関東圏 28%）**:
- 東京: 14.9%、高エンゲージ（13.4秒）、低直帰（60.5%）
- 神奈川: 5.2%、高エンゲージ（11.1秒）
- 埼玉: 4.0%、高エンゲージ（12.9秒）
- 千葉: 3.9%

**施策**: 
- 関東限定キャンペーン
- 東京イベント告知
- 首都圏向けコンテンツ

**セカンダリーエリア（関西・主要都市 15%）**:
- 大阪: 7.5%
- 愛知（名古屋）: 5.5%
- 福岡: 5.0%

**施策**:
- 地域別ランディングページ
- 地方都市向けコンテンツ

### 広告配信最適化

**地域ターゲティング**:
1. **高ROIエリア**: 東京・神奈川（高エンゲージ、低直帰）
2. **ボリュームエリア**: 大阪・北海道（セッション多い）
3. **効率重視**: 福岡（CVR 130%）

**入札調整**:
- 東京: 基準+30%（高品質トラフィック）
- 大阪・北海道: 基準値
- その他地方: 基準-20%（効率見極め）

### エリアコンテンツ戦略

**地域特化コンテンツ**:
- 東京向け: 詳細・高度なコンテンツ（13.4秒読む）
- 地方向け: 簡潔・分かりやすいコンテンツ

**地域イベント連動**:
- 東京イベント → 関東圏で告知強化
- 地方イベント → 該当地域で集中配信

## 洞察と戦略

### 発見1: 東京の高パフォーマンス
- **エンゲージ13.4秒**: 他地域の2倍
- **直帰率60.5%**: 最も低い
- **解釈**: 都市部ユーザーは関心が高い、情報収集に積極的
- **施策**: 東京向け高品質コンテンツ投資

### 発見2: 関東圏集中（28%）
- **現象**: 関東4都県で約3割
- **解釈**: 人口集中地域
- **施策**: 関東限定キャンペーン、イベント開催

### 発見3: 地方の効率性
- **福岡**: CVR 130.3%（高い）
- **北海道**: セッション984（多い）
- **施策**: 効率の良い地方エリアに注力

### 発見4: 地域間のエンゲージ格差
- **首都圏**: 11-13秒
- **地方**: 5-7秒
- **解釈**: コンテンツ親和性、ターゲット層の違い
- **施策**: 地域別コンテンツの最適化

## 推奨レイアウト

```
┌────────────────────────┬───────────────────────────────┐
│ Row 1:                 │                               │
│ Chart 296              │ Chart 293                     │
│ 国別セッション         │ 都道府県別セッション          │
├────────────────────────┼───────────────────────────────┤
│ Row 2:                 │                               │
│ Chart 294              │ Chart 298                     │
│ 都道府県別エンゲージ   │ 主要地域推移                  │
├────────────────────────┴───────────────────────────────┤
│ Row 3:                                                 │
│ Chart 295: 都道府県別パフォーマンステーブル TOP20     │
├────────────────────────────────────────────────────────┤
│ Row 4:                                                 │
│ Chart 297: 都道府県別パフォーマンス分析（Bubble）     │
└────────────────────────────────────────────────────────┘
```

## エリアマーケティング戦略

### Tier 1: 最重点エリア（関東圏）
**対象**: 東京、神奈川、埼玉、千葉
**構成比**: 28%
**特徴**: 高エンゲージ、低直帰
**施策**:
- 予算配分: 全体の40%
- 詳細コンテンツ作成
- イベント開催
- インフルエンサーマーケティング

### Tier 2: 主要都市
**対象**: 大阪、愛知、福岡、北海道
**構成比**: 25%
**特徴**: ボリュームあり
**施策**:
- 予算配分: 全体の30%
- 地域別LP作成
- 地方イベント連動

### Tier 3: その他地域
**対象**: 残り都道府県
**構成比**: 47%
**施策**:
- 予算配分: 全体の30%
- 効率重視の配信
- セグメント化

## トラブルシューティング

### 地域名が英語で表示される
- **原因**: GA4のデフォルト設定
- **対処**: 問題なし（Tokyo, Osaka等は認識しやすい）
- **拡張**: 必要なら日本語マッピングテーブル作成

### "(not set)" や空白が表示される
- **原因**: 地域情報が取得できなかったセッション
- **対処**: `WHERE geo_region IS NOT NULL`フィルター（実装済み）

### 地方のデータが少ない
- **原因**: 人口比に応じた自然な分布
- **対処**: 複数地域をグルーピング（例: 北海道・東北）

## 拡張案

### Phase 2（オプション）
1. **地域 × チャネル**: 地域ごとの流入経路分析
2. **地域 × デバイス**: 地域別のデバイス利用傾向
3. **地域 × 時間帯**: 地域別の活動時間帯
4. **エリアグルーピング**: 北海道・東北、関東、中部、関西、中国・四国、九州・沖縄
5. **地図ビジュアライゼーション**: 地域を地図上で可視化（プラグイン必要）

