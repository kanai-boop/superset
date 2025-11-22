# チャネル × セグメント クロス分析設計書

## 概要
チャネル（流入元）と各種セグメント（デバイス、地域、時間帯、新規/リピーター、曜日）のクロス分析。
多次元での深掘りにより、チャネル別の最適な配信戦略を立案する。

## データソース

### BigQueryビュー: v_ga_sessions

**既存ビュー**を活用（新規作成不要）

#### 使用する列
- `source`, `medium` (STRING) - トラフィックソース
- `device_category` (STRING) - デバイス種類
- `geo_country`, `geo_region` (STRING) - 国・地域
- `session_hour` (INTEGER) - セッション開始時刻（0-23）
- `day_of_week` (STRING) - 曜日名
- `new_vs_returning` (STRING) - 新規/リピーター
- その他KPI列: sessions, users, conversions, engagement, bounce rate

## データの特徴（全期間: 2025-08-02 ～ 2025-11-10）

### チャネル × デバイス

**TOP3組み合わせ**:
1. **Google Ads × mobile**: 2,781セッション（86.5%がmobile）
   - エンゲージ: 10.9秒
   - 直帰率: 86.8%
2. **Google Ads × tablet**: 253セッション
   - 直帰率: 68.8%（mobileより良い）
3. **Google Ads × desktop**: 176セッション
   - エンゲージ: **13.5秒**（最高）
   - 直帰率: **62.5%**（最低）

**洞察**:
- モバイルが圧倒的多数だが、デスクトップの質が高い
- デスクトップユーザーはじっくり閲覧（エンゲージ1.2倍）

### チャネル × 地域

**地域分布**:
- Google Ads × 東京: 432セッション（最大）
- Google Ads × 大阪: 255セッション
- Google Ads × 北海道: 223セッション

**洞察**:
- TOP15がすべてGoogle Ads（広告が全国展開）
- 東京が最大だが、地方にも分散

### チャネル × 時間帯

**ピークタイム**:
- Google Ads × 13時: 669セッション
- Google Ads × 12時: 594セッション
- Google Ads × 11時: 396セッション

**洞察**:
- ランチタイム（12-13時）に集中
- 深夜（0-5時）も一定の流入
- オーガニックは時間帯変動が少ない

### チャネル × 新規/リピーター

**構成比**:
- **Google Ads × 新規**: 3,120セッション（**97.2%**）
  - エンゲージ: 10.4秒
- **Google Ads × リピーター**: 90セッション（2.8%）
  - エンゲージ: **18.7秒**（新規の1.8倍）

**洞察**:
- Google Adsは新規獲得に特化（97.2%）
- リピーターのエンゲージは高いが、母数が少ない

### チャネル × 曜日

**曜日別分布**:
- Google Ads × 日曜: 570セッション（最大）
- Google Ads × 月曜: 538セッション
- Google Ads × 水曜: 369セッション（最低）

**洞察**:
- 日曜・月曜がピーク
- 水曜が谷（35%減）
- 曜日別の入札調整が有効

## Superset実装

### データセット

**Dataset 28**: `v_ga_sessions`（既存）

### ダッシュボード構成

**Dashboard 25**: 「チャネル × セグメント クロス分析」

### チャート一覧

#### Chart 306: チャネル × デバイス構成 TOP10
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
  "show_legend": true
}
```

**積み上げ棒グラフ**: チャネル別のデバイス構成比

#### Chart 307: チャネル × デバイス詳細 TOP30
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
  "row_limit": 30
}
```

#### Chart 308: チャネル × 地域 TOP50
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
  "row_limit": 50
}
```

#### Chart 309: チャネル × 時間帯（主要5チャネル）
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
  "show_legend": true,
  "x_axis_sort_asc": true
}
```

**折れ線グラフ**: チャネル別の時間帯推移

#### Chart 310: チャネル × 新規/リピーター TOP10
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
  "show_legend": true
}
```

#### Chart 311: チャネル × 新規/リピーター詳細 TOP30
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
  "row_limit": 30
}
```

#### Chart 312: チャネル × 曜日 TOP50
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
  "row_limit": 50
}
```

## マーケティング活用方法

### デバイス別最適化

**モバイル向け施策**:
- **現状**: 86.5%のトラフィック、直帰率86.8%
- **課題**: 高い直帰率
- **施策**:
  - ページ速度最適化（AMP対応）
  - 簡潔なコンテンツ
  - モバイルファーストデザイン
  - タップしやすいCTA

**デスクトップ向け施策**:
- **現状**: 質が高い（直帰率62.5%、エンゲージ13.5秒）
- **機会**: 少数だが高品質
- **施策**:
  - 詳細コンテンツ提供
  - デスクトップ限定機能
  - 専用LP作成

### 時間帯別広告配信

**ピークタイム戦略（12-13時）**:
- 入札額: 基準+30%
- 予算配分: 40%
- クリエイティブ: 即効性訴求

**オフピーク戦略（深夜0-5時）**:
- 入札額: 基準-50%
- 予算配分: 10%
- クリエイティブ: 認知拡大

### 曜日別入札調整

**高パフォーマンス曜日（日曜・月曜）**:
- 入札額: 基準+20%
- 予算: 積極配信
- クリエイティブ: CV重視

**低パフォーマンス曜日（水曜）**:
- 入札額: 基準-30%
- 予算: 抑制
- クリエイティブ: テスト配信

### 新規 vs リテンション戦略分離

**新規獲得（Google Ads）**:
- **現状**: 97.2%が新規
- **役割**: 認知・獲得
- **施策**:
  - 検索広告継続
  - ディスプレイ広告拡大
  - LP最適化

**リテンション（別チャネル）**:
- **現状**: リピーター2.8%（エンゲージ1.8倍）
- **役割**: ロイヤリティ向上
- **施策**:
  - メールマーケティング
  - リターゲティング
  - SNSエンゲージメント
  - プッシュ通知

### 地域別戦略

**関東圏（東京・神奈川・埼玉・千葉）**:
- Google Ads: 全国の約25%
- 入札: 基準値
- クリエイティブ: 都市部向け

**地方都市（大阪・北海道・愛知）**:
- Google Ads: 全国の約20%
- 入札: 基準-10%
- クリエイティブ: 地域特化

## 洞察と戦略

### 発見1: モバイル圧倒的だが質に課題
- **現象**: mobile 86.5%、直帰率86.8%
- **解釈**: モバイル体験が最適化されていない
- **施策**: モバイルUX改善が最優先

### 発見2: デスクトップの高品質トラフィック
- **現象**: desktop 5.5%、直帰率62.5%、エンゲージ13.5秒
- **解釈**: 真剣なユーザーはデスクトップ利用
- **施策**: デスクトップ向け詳細コンテンツ

### 発見3: Google Adsが新規獲得に特化
- **現象**: 新規97.2%、リピーター2.8%
- **解釈**: 広告は認知・獲得ツール
- **施策**: リテンション施策を別途構築

### 発見4: 時間帯・曜日で大きな変動
- **現象**: 12-13時がピーク、水曜が谷
- **解釈**: ユーザー行動に明確なパターン
- **施策**: 時間帯・曜日別の入札最適化

### 発見5: 全国展開されている
- **現象**: 全地域にGoogle Ads分散
- **解釈**: 全国向け商材
- **施策**: 地域別クリエイティブ不要（コスト削減）

## 推奨レイアウト

```
┌────────────────────────┬───────────────────────────────┐
│ Row 1:                 │                               │
│ Chart 306              │ Chart 310                     │
│ チャネル×デバイス構成 │ チャネル×新規リピーター構成 │
├────────────────────────┴───────────────────────────────┤
│ Row 2:                                                 │
│ Chart 309: チャネル×時間帯（折れ線、全幅）           │
├────────────────────────────────────────────────────────┤
│ Row 3:                                                 │
│ Chart 307: チャネル×デバイス詳細テーブル（全幅）     │
├────────────────────────┬───────────────────────────────┤
│ Row 4:                 │                               │
│ Chart 311              │ Chart 308                     │
│ チャネル×新規リピ詳細 │ チャネル×地域                │
├────────────────────────┴───────────────────────────────┤
│ Row 5:                                                 │
│ Chart 312: チャネル×曜日（全幅）                      │
└────────────────────────────────────────────────────────┘
```

## 実践的なアクションプラン

### 短期（1ヶ月以内）
1. **時間帯別入札調整**:
   - 12-13時: +30%
   - 0-5時: -50%
2. **曜日別入札調整**:
   - 日曜・月曜: +20%
   - 水曜: -30%
3. **モバイルUX改善**:
   - ページ速度測定
   - CTAボタン最適化

### 中期（3ヶ月以内）
1. **デスクトップ専用LP作成**:
   - 詳細コンテンツ
   - デモ動画
2. **リテンション施策開始**:
   - メルマガ配信
   - リターゲティング広告
3. **デバイス別クリエイティブ**:
   - モバイル: 簡潔
   - デスクトップ: 詳細

### 長期（6ヶ月以内）
1. **モバイルアプリ検討**:
   - リピーター向け
   - プッシュ通知
2. **オムニチャネル戦略**:
   - 広告+メール+SNS統合
   - カスタマージャーニー最適化

## トラブルシューティング

### データが偏っている
- **原因**: Google Adsが圧倒的
- **対処**: 問題なし（実態を反映）
- **拡張**: 他チャネルの強化を検討

### クロス分析が複雑すぎる
- **原因**: 5次元のクロス
- **対処**: 重要な組み合わせに絞る（デバイス×時間帯など）

### セグメントが細かすぎる
- **原因**: 少数データの組み合わせ
- **対処**: 最小セッション数でフィルター（50以上など）

## 拡張案

### Phase 2（オプション）
1. **チャネル × LP**: どのチャネルがどのLPに流入？
2. **チャネル × コンテンツ**: チャネル別の人気コンテンツ
3. **チャネル × CVファネル**: チャネル別のファネル効率
4. **3次元クロス**: チャネル × デバイス × 時間帯
5. **コホート × チャネル**: 初回流入チャネル別のLTV

