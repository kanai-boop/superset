# LLMによるデータ分析・示唆生成の設計

## 概要
ユーザーが自然言語で「今回のキャンペーンを同業他社と比較してどうか教えて」のような指示をした際、マネージドLLMがデータを確認して示唆を出す機能の設計。

---

## 1. 可能なこと vs 制約

### ✅ 可能なこと

1. **自社データの数値読み取り・分析**
   - ✅ **BigQueryからデータの数値自体は読める**
   - BigQueryからデータを取得して分析
   - チャートを作成して可視化
   - データに基づいた数値的な示唆を提供
   - ROAS、CPA、CTRなどのKPI計算

2. **時系列分析**
   - 過去のデータと比較
   - トレンド分析
   - 季節性の検出

3. **指標の計算・比較**
   - 期間比較（前月比、前年比など）
   - チャネル別・デバイス別の比較

### ❌ 制約・課題

1. **同業他社データの取得**
   - ❌ 通常、他社のデータは取得できない
   - ✅ **一般的な業界ベンチマークデータがあれば比較可能**
   - 公開データベースやAPI経由で取得可能な場合のみ対応可能
   - 業界ベンチマークデータが必要な場合は外部サービスを利用
   - 例: eコマース業界の平均ROAS、平均CPAなど

2. **LLMの直接データアクセス**
   - LLMは直接データベースにアクセスできない
   - Function Calling / Tool Use を使用してデータを取得する必要がある

3. **リアルタイム性**
   - BigQueryへのクエリ実行時間がかかる場合がある
   - キャッシュ戦略が必要

### 📝 まとめ

- **自社データの数値**: ✅ 読める（BigQueryから取得可能）
- **同業他社比較**: ⚠️ 一般的なベンチマークデータがあれば可能
  - 例: 「eコマース業界の平均ROASは2.8」のような一般的なデータ
  - 特定の競合他社のデータは取得できない

---

## 2. アーキテクチャ

### 2-1. 全体フロー

```
ユーザー入力
  ↓
LLM（意図理解・ツール選択）
  ↓
Function Calling（BigQueryクエリ実行）
  ↓
データ取得
  ↓
LLM（データ分析・示唆生成）
  ↓
チャート作成（Superset API）
  ↓
ユーザーに返答（テキスト + チャートURL）
```

### 2-2. コンポーネント

1. **Chat Service（FastAPI）**
   - ユーザーからの自然言語入力を受け取る
   - LLM APIを呼び出す
   - Function Callingを管理
   - Superset APIを呼び出してチャートを作成

2. **LLM（OpenAI / Vertex AI）**
   - 意図理解
   - ツール選択（どのデータを取得するか）
   - データ分析・示唆生成

3. **Function Calling / Tool Use**
   - BigQueryクエリ実行
   - Superset API呼び出し
   - 外部API呼び出し（業界ベンチマークなど）

4. **BigQuery**
   - 実際のデータソース
   - クエリ結果を返す

5. **Superset API**
   - チャート作成
   - ダッシュボード作成

---

## 3. 実装例：「キャンペーンを同業他社と比較」

### 3-1. ユーザー入力
```
「今回のキャンペーンを同業他社と比較してどうか教えて」
```

### 3-2. LLMの処理フロー

#### Step 1: 意図理解
```json
{
  "intent": "campaign_comparison",
  "entities": {
    "campaign": "今回のキャンペーン",
    "comparison_target": "同業他社",
    "metrics": ["ROAS", "CPA", "CTR", "Cost"]
  },
  "required_data": [
    "自社キャンペーンデータ",
    "業界ベンチマークデータ（可能な場合）"
  ]
}
```

#### Step 2: Function Calling（自社データ取得）
```python
# LLMが呼び出す関数
def query_campaign_data(
    campaign_name: str,
    date_range: str,
    metrics: list[str]
) -> dict:
    """
    BigQueryからキャンペーンデータを取得
    """
    query = f"""
    SELECT 
      event_date,
      campaign_name,
      SUM(ads_cost) as cost,
      SUM(ads_clicks) as clicks,
      SUM(ads_impressions) as impressions,
      SUM(conversions) as conversions,
      SUM(revenue) as revenue,
      SUM(revenue) / NULLIF(SUM(ads_cost), 0) as roas,
      SUM(ads_cost) / NULLIF(SUM(conversions), 0) as cpa
    FROM `analytics_456071139.v_ga_ads_performance`
    WHERE campaign_name = '{campaign_name}'
      AND event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL {date_range} DAY)
    GROUP BY event_date, campaign_name
    ORDER BY event_date DESC
    """
    
    # BigQueryクエリ実行
    result = bigquery_client.query(query).to_dataframe()
    return result.to_dict('records')
```

#### Step 3: 外部データ取得（業界ベンチマーク）
```python
# 業界ベンチマークデータを取得（可能な場合）
def get_industry_benchmark(
    industry: str,
    metric: str
) -> dict:
    """
    業界ベンチマークデータを取得
    - 公開API経由
    - または、事前に収集したベンチマークデータベースから
    """
    # 例: Google Ads API、Facebook Marketing APIなど
    # または、自社で構築したベンチマークデータベース
    pass
```

#### Step 4: データ分析・示唆生成
```python
# LLMにデータを渡して分析
prompt = f"""
以下のキャンペーンデータを分析して、示唆を提供してください。

【自社データ】
{json.dumps(campaign_data, indent=2)}

【業界ベンチマーク（可能な場合）】
{json.dumps(benchmark_data, indent=2)}

以下の観点で分析してください：
1. 自社のパフォーマンス（ROAS、CPA、CTRなど）
2. 業界平均との比較（可能な場合）
3. 改善提案
4. 注意すべきポイント
"""
```

#### Step 5: チャート作成
```python
# LLMが分析結果に基づいてチャートを作成
def create_comparison_chart(
    campaign_data: dict,
    benchmark_data: dict
) -> str:
    """
    Superset APIを呼び出してチャートを作成
    """
    chart_config = {
        "viz_type": "line",
        "datasource": "27__table",
        "metrics": [
            {"expressionType": "SQL", "sqlExpression": "SUM(ads_cost)", "label": "Cost"},
            {"expressionType": "SQL", "sqlExpression": "SUM(revenue) / NULLIF(SUM(ads_cost), 0)", "label": "ROAS"}
        ],
        "groupby": ["event_date"],
        "adhoc_filters": [{
            "clause": "WHERE",
            "expressionType": "SQL",
            "sqlExpression": f"campaign_name = '{campaign_name}'"
        }]
    }
    
    # Superset API呼び出し
    response = requests.post(
        f"{SUPERSET_URL}/api/v1/chart/",
        headers={"Authorization": f"Bearer {token}"},
        json=chart_config
    )
    
    return response.json()["result"]["url"]
```

#### Step 6: ユーザーへの返答
```json
{
  "text": "今回のキャンペーンの分析結果です。\n\n【パフォーマンス】\n- ROAS: 3.2（業界平均: 2.8）\n- CPA: 1,200円（業界平均: 1,500円）\n- CTR: 2.5%（業界平均: 2.0%）\n\n【示唆】\n1. ROASが業界平均を上回っており、効率的な運用ができています。\n2. CPAも業界平均より低く、コスト効率が良いです。\n3. ただし、CTRは業界平均と同等で、改善の余地があります。\n\n【改善提案】\n- 広告クリエイティブの最適化\n- ターゲティングの見直し\n- A/Bテストの実施",
  "charts": [
    {
      "title": "キャンペーンROAS推移",
      "url": "https://superset.example.com/explore/?chart_id=123"
    },
    {
      "title": "業界平均との比較",
      "url": "https://superset.example.com/explore/?chart_id=124"
    }
  ]
}
```

---

## 4. 実装の詳細

### 4-1. Function Callingの定義

```python
# OpenAI Function Callingの例
functions = [
    {
        "name": "query_bigquery",
        "description": "BigQueryからデータを取得します。キャンペーン、チャネル、デバイスなどのデータを分析する際に使用します。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "実行するSQLクエリ"
                },
                "dataset": {
                    "type": "string",
                    "description": "データセット名（例: v_ga_ads_performance, v_ga_sessions）",
                    "enum": ["v_ga_ads_performance", "v_ga_sessions", "v_ga_content_performance"]
                }
            },
            "required": ["query", "dataset"]
        }
    },
    {
        "name": "create_superset_chart",
        "description": "Supersetでチャートを作成します。データを可視化する際に使用します。",
        "parameters": {
            "type": "object",
            "properties": {
                "viz_type": {
                    "type": "string",
                    "description": "チャートタイプ",
                    "enum": ["line", "bar", "table", "big_number", "bubble"]
                },
                "metrics": {
                    "type": "array",
                    "description": "表示するメトリクス"
                },
                "groupby": {
                    "type": "array",
                    "description": "グループ化するカラム"
                }
            },
            "required": ["viz_type", "metrics"]
        }
    },
    {
        "name": "get_industry_benchmark",
        "description": "業界ベンチマークデータを取得します。同業他社との比較に使用します。",
        "parameters": {
            "type": "object",
            "properties": {
                "industry": {
                    "type": "string",
                    "description": "業界（例: ecommerce, saas, finance）"
                },
                "metric": {
                    "type": "string",
                    "description": "メトリクス（例: ROAS, CPA, CTR）"
                }
            },
            "required": ["industry", "metric"]
        }
    }
]
```

### 4-2. LLMプロンプト設計

```python
system_prompt = """
あなたはデータ分析の専門家です。ユーザーからの質問に対して、以下の手順で回答してください：

1. ユーザーの意図を理解する
2. 必要なデータを特定する
3. BigQueryからデータを取得する（query_bigquery関数を使用）
4. データを分析する
5. 示唆を提供する
6. 必要に応じてチャートを作成する（create_superset_chart関数を使用）

【利用可能なデータセット】
- v_ga_ads_performance: Google Adsパフォーマンスデータ
- v_ga_sessions: セッションデータ
- v_ga_content_performance: コンテンツパフォーマンスデータ

【注意事項】
- テナントIDごとにアクセス可能なデータセットが異なります
- 他テナントのデータにアクセスしないでください
- SQLインジェクション対策のため、パラメータ化クエリを使用してください
"""
```

### 4-3. エラーハンドリング

```python
def handle_llm_response(response: dict) -> dict:
    """
    LLMの応答を処理し、エラーをハンドリング
    """
    if "function_call" in response:
        function_name = response["function_call"]["name"]
        function_args = json.loads(response["function_call"]["arguments"])
        
        try:
            if function_name == "query_bigquery":
                result = query_bigquery(**function_args)
            elif function_name == "create_superset_chart":
                result = create_superset_chart(**function_args)
            elif function_name == "get_industry_benchmark":
                result = get_industry_benchmark(**function_args)
            else:
                raise ValueError(f"Unknown function: {function_name}")
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "データの取得に失敗しました。別の方法を試してください。"
            }
    
    return {
        "success": True,
        "text": response["content"]
    }
```

---

## 5. 同業他社データの取得方法

### 5-1. 公開データベース・API

1. **Google Ads API**
   - 業界平均データを取得可能（制限あり）
   - 自社アカウントのデータのみ

2. **Facebook Marketing API**
   - 業界平均データを取得可能（制限あり）
   - 自社アカウントのデータのみ

3. **業界レポート**
   - 公開されている業界レポートからデータを抽出
   - 例: eMarketer、Statistaなど

### 5-2. 自社で構築するベンチマークデータベース

```sql
-- ベンチマークデータテーブル
CREATE TABLE `analytics_456071139.industry_benchmarks` (
  industry STRING,
  metric STRING,
  value FLOAT64,
  date DATE,
  source STRING
);

-- データ投入（手動または自動）
INSERT INTO `analytics_456071139.industry_benchmarks` VALUES
  ('ecommerce', 'ROAS', 2.8, '2025-01-01', 'industry_report'),
  ('ecommerce', 'CPA', 1500, '2025-01-01', 'industry_report'),
  ('ecommerce', 'CTR', 2.0, '2025-01-01', 'industry_report');
```

### 5-3. 代替案：相対比較

同業他社データが取得できない場合：
- 自社の過去データと比較
- チャネル間の比較
- デバイス間の比較
- 地域間の比較

---

## 6. セキュリティ・プライバシー

### 6-1. データアクセス制御

```python
def check_tenant_access(tenant_id: str, dataset: str) -> bool:
    """
    テナントがデータセットにアクセス可能かチェック
    """
    allowed_datasets = get_tenant_allowed_datasets(tenant_id)
    return dataset in allowed_datasets
```

### 6-2. SQLインジェクション対策

```python
def execute_safe_query(query: str, params: dict) -> pd.DataFrame:
    """
    パラメータ化クエリでSQLインジェクションを防止
    """
    # パラメータ化クエリを使用
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("campaign_name", "STRING", params["campaign_name"]),
            bigquery.ScalarQueryParameter("start_date", "DATE", params["start_date"])
        ]
    )
    
    query = """
    SELECT * FROM `analytics_456071139.v_ga_ads_performance`
    WHERE campaign_name = @campaign_name
      AND event_date >= @start_date
    """
    
    return bigquery_client.query(query, job_config=job_config).to_dataframe()
```

### 6-3. ログ・監査

```python
def log_llm_query(tenant_id: str, user_id: str, query: str, result: dict):
    """
    LLMクエリをログに記録
    """
    log_entry = {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "query": query,
        "result_size": len(result),
        "timestamp": datetime.now().isoformat()
    }
    
    # BigQuery Audit Logに記録
    bigquery_client.insert_rows_json("audit.llm_queries", [log_entry])
```

---

## 7. パフォーマンス最適化

### 7-1. キャッシュ戦略

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_bigquery_query(query_hash: str, query: str) -> pd.DataFrame:
    """
    クエリ結果をキャッシュ
    """
    # Redisなどにキャッシュ
    cache_key = f"bq_query:{query_hash}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return pd.read_json(cached_result)
    
    result = bigquery_client.query(query).to_dataframe()
    redis_client.setex(cache_key, 3600, result.to_json())  # 1時間キャッシュ
    
    return result
```

### 7-2. 非同期処理

```python
async def process_llm_request(user_input: str) -> dict:
    """
    非同期でLLMリクエストを処理
    """
    # LLM呼び出し
    llm_response = await llm_client.chat.completions.create_async(
        model="gpt-4",
        messages=[{"role": "user", "content": user_input}],
        functions=functions
    )
    
    # Function Calling実行
    if llm_response.choices[0].message.function_call:
        function_result = await execute_function_async(
            llm_response.choices[0].message.function_call
        )
        
        # 結果をLLMに返す
        final_response = await llm_client.chat.completions.create_async(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": None, "function_call": llm_response.choices[0].message.function_call},
                {"role": "function", "name": function_result["name"], "content": json.dumps(function_result["result"])}
            ]
        )
        
        return final_response.choices[0].message.content
    
    return llm_response.choices[0].message.content
```

---

## 8. まとめ

### 可能なこと
- ✅ 自社データの分析・示唆生成
- ✅ チャートの自動生成
- ✅ 時系列分析・比較
- ✅ 指標の計算・比較

### 制約
- ❌ 同業他社データは通常取得できない（公開データベース・API経由のみ）
- ❌ LLMは直接データベースにアクセスできない（Function Callingが必要）
- ❌ リアルタイム性に制約がある場合がある

### 実装のポイント
1. **Function Calling**を使用してデータを取得
2. **セキュリティ**を徹底（テナント分離、SQLインジェクション対策）
3. **パフォーマンス**を最適化（キャッシュ、非同期処理）
4. **エラーハンドリング**を適切に実装

### 推奨実装順序
1. **フェーズ1**: 自社データの分析・示唆生成（Function Calling + BigQuery）
2. **フェーズ2**: チャート自動生成（Superset API連携）
3. **フェーズ3**: 業界ベンチマークデータの統合（可能な場合）

