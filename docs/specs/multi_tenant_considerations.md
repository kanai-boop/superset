# マルチテナントSaaS展開 追加考慮事項

## 概要
マルチテナントSaaSとしてSupersetを展開する際に考慮すべき追加事項をまとめる。

---

## 1. パフォーマンス・スケーラビリティ

### 1-1. 同時アクセスへの対応

#### 課題
- 複数テナントが同時にアクセスした場合のパフォーマンス低下
- BigQueryへの同時クエリ数の制限
- Supersetインスタンスのリソース制約

#### 対策

**キャッシュ戦略**
```python
# Redisキャッシュの設定
CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": "redis://redis:6379/0",
    "CACHE_DEFAULT_TIMEOUT": 300,  # 5分
    "CACHE_KEY_PREFIX": "superset_"
}

# テナントごとのキャッシュキー
def get_cache_key(tenant_id: str, chart_id: int) -> str:
    return f"tenant:{tenant_id}:chart:{chart_id}"
```

**クエリキューイング**
```python
# Celery Workerでクエリをキューイング
@celery_app.task
def execute_bigquery_query(query: str, tenant_id: str):
    """BigQueryクエリを非同期実行"""
    # テナントごとのクエリ制限
    # レート制限の実装
    pass
```

**接続プール**
```python
# SQLAlchemy接続プールの設定
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 20,
    "max_overflow": 10,
    "pool_pre_ping": True,
    "pool_recycle": 3600
}
```

### 1-2. スケーリング戦略

- **水平スケーリング**: Cloud Runの自動スケーリング
- **読み取りレプリカ**: Cloud SQLの読み取りレプリカで負荷分散
- **CDN**: 静的コンテンツの配信

---

## 2. コスト管理

### 2-1. BigQueryクエリコスト

#### 課題
- BigQueryのクエリコストがテナントごとに異なる
- 予期しない高額請求のリスク

#### 対策

**クエリコストの追跡**
```python
class QueryCostTracker:
    def track_query_cost(
        self,
        tenant_id: str,
        query: str,
        bytes_processed: int
    ):
        """クエリコストを追跡"""
        cost = bytes_processed * 0.000005  # $5/TB
        
        # BigQuery Audit Logに記録
        self.log_to_bigquery({
            "tenant_id": tenant_id,
            "query": query,
            "bytes_processed": bytes_processed,
            "cost": cost,
            "timestamp": datetime.now()
        })
```

**クエリ制限**
```python
# テナントごとのクエリ制限
TENANT_QUERY_LIMITS = {
    "customer_a": {
        "daily_bytes_limit": 100 * 1024 * 1024 * 1024,  # 100GB/日
        "monthly_bytes_limit": 3 * 1024 * 1024 * 1024 * 1024  # 3TB/月
    }
}

def check_query_limit(tenant_id: str, estimated_bytes: int) -> bool:
    """クエリ制限をチェック"""
    limits = TENANT_QUERY_LIMITS.get(tenant_id, {})
    daily_limit = limits.get("daily_bytes_limit", 0)
    
    # 今日の使用量を取得
    today_usage = get_daily_usage(tenant_id)
    
    if today_usage + estimated_bytes > daily_limit:
        raise QueryLimitExceededError("Daily query limit exceeded")
    
    return True
```

### 2-2. 課金システム

**テナントごとのコスト集計**
```python
def calculate_tenant_cost(tenant_id: str, month: str) -> Dict:
    """テナントの月次コストを計算"""
    # BigQueryクエリコスト
    query_cost = get_bigquery_cost(tenant_id, month)
    
    # Cloud SQLコスト（共有の場合）
    db_cost = get_database_cost(tenant_id, month)
    
    # Cloud Runコスト（共有の場合）
    compute_cost = get_compute_cost(tenant_id, month)
    
    return {
        "tenant_id": tenant_id,
        "month": month,
        "query_cost": query_cost,
        "database_cost": db_cost,
        "compute_cost": compute_cost,
        "total_cost": query_cost + db_cost + compute_cost
    }
```

---

## 3. 監視・アラート

### 3-1. システム監視

**メトリクス**
- CPU使用率
- メモリ使用率
- リクエスト数
- エラー率
- レスポンスタイム

**実装例**
```python
# Prometheusメトリクス
from prometheus_client import Counter, Histogram

request_count = Counter(
    'superset_requests_total',
    'Total number of requests',
    ['tenant_id', 'endpoint', 'status']
)

request_duration = Histogram(
    'superset_request_duration_seconds',
    'Request duration',
    ['tenant_id', 'endpoint']
)
```

### 3-2. エラー監視

**エラートラッキング**
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
    environment="production"
)

# テナント情報をコンテキストに追加
def set_tenant_context(tenant_id: str):
    sentry_sdk.set_context("tenant", {"id": tenant_id})
```

### 3-3. アラート設定

**アラート条件**
- エラー率が閾値を超えた場合
- レスポンスタイムが閾値を超えた場合
- クエリコストが予算を超えた場合
- ディスク使用率が閾値を超えた場合

---

## 4. バックアップ・災害復旧

### 4-1. データバックアップ

**バックアップ戦略**
- **日次バックアップ**: Cloud SQLの自動バックアップ
- **週次エクスポート**: Supersetメタデータのエクスポート
- **月次アーカイブ**: 長期保存用のアーカイブ

**実装例**
```python
def backup_tenant_data(tenant_id: str):
    """テナントデータをバックアップ"""
    # 1. ダッシュボード・チャートをエクスポート
    dashboards = get_tenant_dashboards(tenant_id)
    export_dashboards(dashboards, f"backup/{tenant_id}/dashboards.json")
    
    # 2. データベース接続情報をバックアップ
    database = get_tenant_database(tenant_id)
    backup_database_config(database, f"backup/{tenant_id}/database.json")
    
    # 3. ユーザー情報をバックアップ
    users = get_tenant_users(tenant_id)
    backup_users(users, f"backup/{tenant_id}/users.json")
```

### 4-2. 災害復旧計画

**RTO（Recovery Time Objective）**: 4時間以内
**RPO（Recovery Point Objective）**: 24時間以内

**復旧手順**
1. Cloud SQLバックアップから復元
2. Supersetメタデータをインポート
3. 設定を復元
4. 動作確認

---

## 5. セキュリティ

### 5-1. データ暗号化

**転送中の暗号化**
- HTTPS/TLS 1.3を使用
- Cloud RunのデフォルトTLS証明書を使用

**保存時の暗号化**
- Cloud SQLの暗号化機能を使用
- BigQueryの暗号化機能を使用

### 5-2. ネットワークセキュリティ

**VPC設定**
- Cloud RunとCloud SQLをVPC内に配置
- Private Service Connectを使用
- パブリックアクセスを制限

### 5-3. コンプライアンス

**対応が必要な規制**
- GDPR（EU一般データ保護規則）
- SOC 2
- ISO 27001

**実装例**
```python
# データ保持ポリシー
DATA_RETENTION_POLICY = {
    "default": 365,  # 1年
    "gdpr": 90,  # GDPR準拠の場合は90日
}

def delete_old_data(tenant_id: str):
    """古いデータを削除（GDPR準拠）"""
    retention_days = DATA_RETENTION_POLICY.get("default", 365)
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    # 古いデータを削除
    delete_old_charts(tenant_id, cutoff_date)
    delete_old_dashboards(tenant_id, cutoff_date)
```

---

## 6. オンボーディング・サポート

### 6-1. お客さん向けドキュメント

**必要なドキュメント**
- ログイン方法
- ダッシュボードの使い方
- チャートの作成方法
- よくある質問（FAQ）

### 6-2. サポート体制

**サポートチャネル**
- メールサポート
- チャットサポート（オプション）
- 電話サポート（オプション）

**サポートレベル**
- **レベル1**: 基本的な質問・トラブルシューティング
- **レベル2**: 技術的な問題・設定変更
- **レベル3**: 緊急対応・システム障害

### 6-3. フィードバック収集

**フィードバック方法**
- アンケートフォーム
- フィードバックボタン（UI内）
- 定期的な顧客インタビュー

---

## 7. アップグレード・メンテナンス

### 7-1. Supersetのアップグレード戦略

**アップグレード手順**
1. ステージング環境でテスト
2. バックアップを取得
3. メンテナンスモードに移行
4. アップグレードを実行
5. 動作確認
6. メンテナンスモードを解除

**ダウンのタイム管理**
- メンテナンスウィンドウを事前に通知
- お客さんに影響を最小限に

### 7-2. メンテナンス計画

**定期メンテナンス**
- 週次: ログローテーション
- 月次: データベース最適化
- 四半期: セキュリティパッチ適用

---

## 8. データ品質・バリデーション

### 8-1. データの整合性チェック

**チェック項目**
- BigQuery Viewの存在確認
- カラムの存在確認
- データ型の整合性

**実装例**
```python
def validate_tenant_data(tenant_id: str) -> List[str]:
    """テナントデータの整合性をチェック"""
    errors = []
    
    # Database接続の確認
    database = get_tenant_database(tenant_id)
    if not test_database_connection(database):
        errors.append(f"Database connection failed for {tenant_id}")
    
    # Datasetの存在確認
    datasets = get_tenant_datasets(tenant_id)
    required_datasets = ["v_ga_ads_performance", "v_ga_sessions"]
    for dataset_name in required_datasets:
        if dataset_name not in datasets:
            errors.append(f"Required dataset {dataset_name} not found")
    
    return errors
```

### 8-2. エラーハンドリング

**エラー処理**
- ユーザーフレンドリーなエラーメッセージ
- エラーログの記録
- 自動リトライ（可能な場合）

---

## 9. APIレート制限

### 9-1. テナントごとのAPI使用制限

**実装例**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=lambda: get_tenant_id_from_request(),
    default_limits=["1000 per hour"]
)

# テナントごとの制限
TENANT_RATE_LIMITS = {
    "customer_a": "5000 per hour",
    "customer_b": "2000 per hour",
}

@limiter.limit(lambda: TENANT_RATE_LIMITS.get(get_tenant_id(), "1000 per hour"))
def api_endpoint():
    pass
```

### 9-2. スロットリング

**実装例**
```python
def throttle_requests(tenant_id: str) -> bool:
    """リクエストをスロットリング"""
    # レート制限をチェック
    if is_rate_limit_exceeded(tenant_id):
        return False
    
    # クエリキューが満杯の場合
    if is_query_queue_full(tenant_id):
        return False
    
    return True
```

---

## 10. マルチリージョン対応（将来）

### 10-1. データの地理的分散

**考慮事項**
- データのレプリケーション
- レイテンシーの最適化
- コストの増加

### 10-2. 実装方針

**フェーズ1**: 単一リージョン（東京）
**フェーズ2**: マルチリージョン（東京 + 大阪）
**フェーズ3**: グローバル展開（必要に応じて）

---

## 11. その他の考慮事項

### 11-1. ログ管理

**ログの種類**
- アクセスログ
- エラーログ
- 監査ログ
- パフォーマンスログ

**ログの保存**
- Cloud Loggingに集約
- BigQueryにエクスポート（長期保存）
- ログローテーション（30日間保持）

### 11-2. テスト戦略

**テストの種類**
- ユニットテスト
- 統合テスト
- E2Eテスト
- 負荷テスト

**テスト環境**
- 開発環境
- ステージング環境
- 本番環境

### 11-3. ドキュメント管理

**必要なドキュメント**
- アーキテクチャドキュメント
- APIドキュメント
- 運用マニュアル
- トラブルシューティングガイド

---

## 12. 優先順位付け

### 高優先度（必須）
1. ✅ パフォーマンス・スケーラビリティ（キャッシュ戦略）
2. ✅ コスト管理（BigQueryクエリコスト追跡）
3. ✅ 監視・アラート（基本的な監視）
4. ✅ バックアップ・災害復旧（日次バックアップ）
5. ✅ セキュリティ（基本的なセキュリティ対策）

### 中優先度（重要）
6. ⚠️ オンボーディング・サポート（基本的なドキュメント）
7. ⚠️ アップグレード・メンテナンス（アップグレード手順）
8. ⚠️ データ品質・バリデーション（基本的なチェック）

### 低優先度（将来対応）
9. 📋 APIレート制限（必要に応じて）
10. 📋 マルチリージョン対応（将来の拡張）

---

## まとめ

マルチテナントSaaSとしてSupersetを展開する際は、以下の点を考慮する必要があります：

1. **パフォーマンス**: キャッシュ戦略、スケーリング
2. **コスト**: BigQueryクエリコストの追跡・制限
3. **監視**: システム監視、エラー監視、アラート
4. **バックアップ**: データバックアップ、災害復旧計画
5. **セキュリティ**: 暗号化、ネットワークセキュリティ、コンプライアンス
6. **サポート**: ドキュメント、サポート体制、フィードバック収集
7. **メンテナンス**: アップグレード戦略、メンテナンス計画
8. **品質**: データ品質チェック、エラーハンドリング

優先順位を付けて、段階的に実装していくことを推奨します。

