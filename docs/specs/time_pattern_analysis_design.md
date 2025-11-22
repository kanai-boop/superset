# 時間帯・曜日パターン分析設計書

## 概要
ユーザーの訪問時間帯・曜日パターンを分析し、コンテンツ配信・広告配信の最適タイミングを特定する。

## データソース

### BigQueryビュー: v_ga_sessions

**既存ビューを拡張**

#### 追加された列
- `session_hour` (INTEGER) - セッション開始時刻（0-23時）
- `day_of_week` (STRING) - 曜日名（日曜日～土曜日）
- `day_of_week_num` (INTEGER) - 曜日番号（1=日曜, 7=土曜）
- `weekday_weekend` (STRING) - "平日" または "週末"

#### 抽出ロジック
```sql
EXTRACT(HOUR FROM session_start_timestamp) AS session_hour,
EXTRACT(DAYOFWEEK FROM session_start_timestamp) AS day_of_week_num,
CASE EXTRACT(DAYOFWEEK FROM session_start_timestamp)
  WHEN 1 THEN '日曜日'
  WHEN 2 THEN '月曜日'
  ...
  WHEN 7 THEN '土曜日'
END AS day_of_week,
CASE 
  WHEN EXTRACT(DAYOFWEEK FROM session_start_timestamp) IN (1, 7) THEN '週末'
  ELSE '平日'
END AS weekday_weekend
```

## データの特徴（全期間: 2025-08-02 ～ 2025-11-10）

### 曜日パターン

**セッション数**:
- 日曜日: 2,287（16.0%）
- 月曜日: 2,029（14.2%）
- 火曜日: 2,175（15.2%）← ピーク
- 水曜日: 1,886（13.2%）← 谷
- 木曜日: 1,891（13.2%）
- 金曜日: 2,065（14.4%）
- 土曜日: 2,022（14.1%）

**エンゲージメント時間**:
- 水曜日: 11.1秒（最高）✨
- 金曜日: 10.6秒
- 火曜日: 9.5秒
- 土曜日: 7.1秒
- 日曜日: 5.8秒（最低）

**直帰率**:
- 火曜日: 63.8%（最低）✅
- 水曜日: 67.1%
- 日曜日: 72.1%（最高）

### 時間帯パターン

**ピークタイム**:
1. **12時台**: 2,083セッション（14.6%）← 最大ピーク
2. **13時台**: 1,856セッション（13.0%）
3. **11時台**: 1,510セッション（10.6%）

**セカンダリーピーク**:
- 14時台: 934セッション
- 10時台: 933セッション

**オフピーク**:
- 深夜0-5時: 合計約2,500セッション
- 夜間18-23時: 比較的少ない

### 平日 vs 週末

| 指標 | 平日 | 週末 | 差分 |
|------|------|------|------|
| Sessions | 10,046 (70.0%) | 4,309 (30.0%) | +133% |
| Users | 6,514 | 3,101 | +110% |
| CVs | 10,986 | 4,685 | +134% |
| Avg Engagement | 9.4秒 | 6.4秒 | +47% |
| Bounce Rate | 67.9% | 71.1% | -3.2pt |

**結論**: 平日の方が量・質ともに優れている

## Superset実装

### データセット

**Dataset 28**: `v_ga_sessions`（拡張版）
- 新規列: `session_hour`, `day_of_week`, `day_of_week_num`, `weekday_weekend`

### ダッシュボード構成

**Dashboard 22**: 「時間帯・曜日パターン分析」

### チャート一覧

#### Chart 287: 曜日別セッション数
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "day_of_week",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  }],
  "orientation": "vertical",
  "y_axis_format": ",d"
}
```

**縦棒グラフ**: 曜日ごとのトラフィック量を可視化

#### Chart 288: 時間帯別セッション数
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
  "y_axis_format": ",d",
  "x_axis_sort_asc": true
}
```

**折れ線グラフ**: 0-23時の時間帯推移を可視化

#### Chart 289: 平日 vs 週末比較
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": ["weekday_weekend"],
  "metrics": [
    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Sessions"},
    {"expressionType": "SQL", "sqlExpression": "COUNT(DISTINCT user_pseudo_id)", "label": "Users"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions)", "label": "Conversions"},
    {"expressionType": "SQL", "sqlExpression": "AVG(total_engagement_time_msec / 1000)", "label": "Avg Engagement (sec)"},
    {"expressionType": "SQL", "sqlExpression": "COUNTIF(session_pageviews = 1) / NULLIF(COUNT(*), 0) * 100", "label": "Bounce Rate (%)"},
    {"expressionType": "SQL", "sqlExpression": "SUM(conversions) / NULLIF(COUNT(*), 0) * 100", "label": "CVR (%)"}
  ]
}
```

#### Chart 290: 曜日別平均エンゲージメント時間
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "28__table",
  "x_axis": "day_of_week",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "AVG(total_engagement_time_msec / 1000)",
    "label": "Avg Engagement (sec)"
  }],
  "orientation": "horizontal",
  "y_axis_format": ".1f"
}
```

#### Chart 291: 時間×曜日マトリクス
```json
{
  "viz_type": "table",
  "datasource": "28__table",
  "query_mode": "aggregate",
  "groupby": ["day_of_week", "session_hour"],
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "COUNT(*)",
    "label": "Sessions"
  }],
  "row_limit": 200
}
```

**ヒートマップ的な表示**: 曜日×時間のセッション分布

#### Chart 292: 時間帯別CVR
```json
{
  "viz_type": "echarts_timeseries_line",
  "datasource": "28__table",
  "x_axis": "session_hour",
  "metrics": [{
    "expressionType": "SQL",
    "sqlExpression": "SUM(conversions) / NULLIF(COUNT(*), 0) * 100",
    "label": "CVR (%)"
  }],
  "y_axis_format": ".1f",
  "x_axis_sort_asc": true
}
```

## マーケティング活用方法

### コンテンツ配信最適化
1. **ブログ・記事公開**: 平日12-13時（ピークタイム）
2. **メール配信**: 火曜・水曜の11時（高エンゲージ）
3. **プッシュ通知**: 平日ランチタイム

### 広告配信スケジュール
1. **予算集中**: 平日11-14時（70%のトラフィック）
2. **入札調整**: 
   - 高入札: 火曜・水曜12-13時
   - 低入札: 週末・深夜
3. **デイパーティング**: 時間帯別の入札最適化

### カスタマーサポート
1. **人員配置**: 平日12-14時を手厚く
2. **チャットボット**: 夜間・週末に活用
3. **問い合わせ対応**: 水曜日を優先（高エンゲージユーザー）

### A/Bテスト実施タイミング
1. **最適期間**: 火曜-木曜の11-14時
   - 安定したトラフィック
   - 高エンゲージメント
2. **避けるべき**: 週末（行動パターンが異なる）

## 洞察と戦略

### 発見1: ランチタイム集中（12-13時）
- **現象**: 最大ピークがランチタイム
- **解釈**: 仕事の休憩時間に閲覧
- **施策**: ランチタイム限定オファー、短時間で読めるコンテンツ

### 発見2: 水曜日の高エンゲージメント（11.1秒）
- **現象**: エンゲージメントが最も高い
- **解釈**: 週の中日、じっくり読む時間がある
- **施策**: 詳細コンテンツは水曜配信、重要発表も水曜

### 発見3: 平日 vs 週末の質の違い
- **平日**: 高エンゲージ（9.4秒）、低直帰（67.9%）
- **週末**: 低エンゲージ（6.4秒）、高直帰（71.1%）
- **解釈**: 平日は目的意識が高い、週末はカジュアル閲覧
- **施策**: 
  - 平日: コンバージョン重視の施策
  - 週末: 認知拡大・エンゲージメント向上

### 発見4: 夜間トラフィックの少なさ
- **現象**: 18時以降が少ない
- **解釈**: ターゲット層が夜は別の活動をしている
- **施策**: 夜間の広告予算を削減、昼間に集中

## 推奨レイアウト

```
┌────────────────────────┬───────────────────────────────┐
│ Row 1:                 │                               │
│ Chart 287              │ Chart 290                     │
│ 曜日別セッション数     │ 曜日別エンゲージメント        │
├────────────────────────┼───────────────────────────────┤
│ Row 2:                 │                               │
│ Chart 288              │ Chart 292                     │
│ 時間帯別セッション     │ 時間帯別CVR                   │
├────────────────────────┼───────────────────────────────┤
│ Row 3:                 │                               │
│ Chart 289              │ Chart 291                     │
│ 平日週末比較           │ 時間×曜日マトリクス           │
└────────────────────────┴───────────────────────────────┘
```

## トラブルシューティング

### 曜日の並び順がおかしい
- **原因**: アルファベット順でソートされている
- **対処**: `day_of_week_num`でソート（実装済み）

### タイムゾーンがずれている
- **原因**: `session_start_timestamp`がUTC
- **確認**: 実際の時間帯と比較して検証
- **対処**: 必要に応じてJSTに変換

### 時間×曜日マトリクスが見づらい
- **原因**: 168行（24時×7日）のテーブル
- **代替**: ヒートマップビジュアライゼーション（プラグイン必要）

## 拡張案

### Phase 2（オプション）
1. **デバイス × 時間帯**: デバイスごとの利用時間帯
2. **チャネル × 曜日**: チャネルごとの最適曜日
3. **新規/リピーター × 時間帯**: ユーザータイプ別の行動パターン
4. **季節性分析**: 月別の曜日パターン変化

