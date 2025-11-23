# テンプレート管理・保護設計

## 概要
お客さんが自然言語で作成したチャート・ダッシュボードを分析してテンプレート化し、テンプレートを保護する仕組みの設計。

---

## 1. 要件

### 1-1. テンプレート化のための分析
- お客さんが自然言語で作成したチャート・ダッシュボードを分析
- よく作られているものをテンプレートに追加
- 何を作っているのか把握

### 1-2. テンプレートの保護
- テンプレートから作成されたダッシュボード・チャートは保護（編集・削除を制限）
- チャートは作成できるが、ダッシュボードの作成は手動（または制限）
- テンプレートを壊さないようにする

---

## 2. テンプレート化のための分析

### 2-1. チャート・ダッシュボードの使用状況分析

#### 分析対象
- チャートの種類（`viz_type`）
- 使用されているメトリクス
- 使用されているデータセット
- ダッシュボードの構成
- 作成頻度

#### 実装例

```python
from collections import Counter
from datetime import datetime, timedelta
import json

class ChartUsageAnalyzer:
    def __init__(self, superset_url: str, admin_token: str):
        self.superset_url = superset_url
        self.admin_token = admin_token
        self.headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
    
    def analyze_chart_usage(
        self,
        days: int = 30,
        min_usage_count: int = 3
    ) -> Dict:
        """
        チャートの使用状況を分析
        
        Args:
            days: 分析期間（日数）
            min_usage_count: テンプレート化の閾値（この回数以上作成されたらテンプレート候補）
        """
        # 全チャートを取得
        charts = self.get_all_charts()
        
        # 分析期間内に作成されたチャートをフィルタ
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_charts = [
            chart for chart in charts
            if datetime.fromisoformat(chart["changed_on"].replace("Z", "+00:00")) >= cutoff_date
        ]
        
        # チャートタイプ別の集計
        chart_type_counter = Counter([c["viz_type"] for c in recent_charts])
        
        # メトリクス別の集計
        metrics_counter = Counter()
        for chart in recent_charts:
            params = json.loads(chart.get("params", "{}"))
            metrics = params.get("metrics", [])
            for metric in metrics:
                if isinstance(metric, dict):
                    metric_label = metric.get("label", str(metric))
                else:
                    metric_label = str(metric)
                metrics_counter[metric_label] += 1
        
        # データセット別の集計
        dataset_counter = Counter([c["datasource_id"] for c in recent_charts])
        
        # テンプレート候補を抽出
        template_candidates = self.extract_template_candidates(
            recent_charts=recent_charts,
            chart_type_counter=chart_type_counter,
            metrics_counter=metrics_counter,
            min_usage_count=min_usage_count
        )
        
        return {
            "analysis_period_days": days,
            "total_charts_created": len(recent_charts),
            "chart_types": dict(chart_type_counter),
            "popular_metrics": dict(metrics_counter.most_common(20)),
            "popular_datasets": dict(dataset_counter.most_common(10)),
            "template_candidates": template_candidates
        }
    
    def get_all_charts(self) -> List[Dict]:
        """全チャートを取得"""
        response = requests.get(
            f"{self.superset_url}/api/v1/chart/?q=(page_size:1000)",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["result"]
    
    def extract_template_candidates(
        self,
        recent_charts: List[Dict],
        chart_type_counter: Counter,
        metrics_counter: Counter,
        min_usage_count: int
    ) -> List[Dict]:
        """テンプレート候補を抽出"""
        candidates = []
        
        # よく使われているチャートタイプを抽出
        popular_chart_types = [
            chart_type for chart_type, count in chart_type_counter.items()
            if count >= min_usage_count
        ]
        
        # 各チャートタイプごとに、よく使われているパターンを抽出
        for chart_type in popular_chart_types:
            type_charts = [c for c in recent_charts if c["viz_type"] == chart_type]
            
            # パラメータパターンを集計
            param_patterns = {}
            for chart in type_charts:
                params = json.loads(chart.get("params", "{}"))
                # パラメータのハッシュを作成（メトリクス、グループ化など）
                pattern_key = self.create_param_pattern_key(params)
                
                if pattern_key not in param_patterns:
                    param_patterns[pattern_key] = {
                        "count": 0,
                        "charts": [],
                        "params": params
                    }
                param_patterns[pattern_key]["count"] += 1
                param_patterns[pattern_key]["charts"].append(chart)
            
            # よく使われているパターンを抽出
            for pattern_key, pattern_data in param_patterns.items():
                if pattern_data["count"] >= min_usage_count:
                    candidates.append({
                        "chart_type": chart_type,
                        "usage_count": pattern_data["count"],
                        "params": pattern_data["params"],
                        "sample_chart_ids": [c["id"] for c in pattern_data["charts"][:5]]
                    })
        
        # 使用回数でソート
        candidates.sort(key=lambda x: x["usage_count"], reverse=True)
        
        return candidates
    
    def create_param_pattern_key(self, params: Dict) -> str:
        """パラメータパターンのキーを作成"""
        # メトリクス、グループ化、フィルタなどを組み合わせてキーを作成
        metrics = sorted([str(m) for m in params.get("metrics", [])])
        groupby = sorted([str(g) for g in params.get("groupby", [])])
        filters = sorted([str(f) for f in params.get("adhoc_filters", [])])
        
        return f"{metrics}|{groupby}|{filters}"
    
    def analyze_dashboard_usage(
        self,
        days: int = 30,
        min_usage_count: int = 2
    ) -> Dict:
        """ダッシュボードの使用状況を分析"""
        # 全ダッシュボードを取得
        dashboards = self.get_all_dashboards()
        
        # 分析期間内に作成されたダッシュボードをフィルタ
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_dashboards = [
            dash for dash in dashboards
            if datetime.fromisoformat(dash["changed_on"].replace("Z", "+00:00")) >= cutoff_date
        ]
        
        # ダッシュボードの構成を分析
        dashboard_patterns = {}
        for dashboard in recent_dashboards:
            # チャートの種類と数を集計
            chart_types = self.get_dashboard_chart_types(dashboard["id"])
            pattern_key = "|".join(sorted(chart_types))
            
            if pattern_key not in dashboard_patterns:
                dashboard_patterns[pattern_key] = {
                    "count": 0,
                    "dashboards": [],
                    "chart_types": chart_types
                }
            dashboard_patterns[pattern_key]["count"] += 1
            dashboard_patterns[pattern_key]["dashboards"].append(dashboard)
        
        # テンプレート候補を抽出
        template_candidates = [
            {
                "usage_count": pattern_data["count"],
                "chart_types": pattern_data["chart_types"],
                "sample_dashboard_ids": [d["id"] for d in pattern_data["dashboards"][:3]]
            }
            for pattern_key, pattern_data in dashboard_patterns.items()
            if pattern_data["count"] >= min_usage_count
        ]
        
        template_candidates.sort(key=lambda x: x["usage_count"], reverse=True)
        
        return {
            "analysis_period_days": days,
            "total_dashboards_created": len(recent_dashboards),
            "dashboard_patterns": dict(dashboard_patterns),
            "template_candidates": template_candidates
        }
    
    def get_all_dashboards(self) -> List[Dict]:
        """全ダッシュボードを取得"""
        response = requests.get(
            f"{self.superset_url}/api/v1/dashboard/?q=(page_size:1000)",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["result"]
    
    def get_dashboard_chart_types(self, dashboard_id: int) -> List[str]:
        """ダッシュボードに含まれるチャートタイプを取得"""
        response = requests.get(
            f"{self.superset_url}/api/v1/dashboard/{dashboard_id}",
            headers=self.headers
        )
        response.raise_for_status()
        dashboard = response.json()["result"]
        
        chart_types = []
        for chart in dashboard.get("slices", []):
            chart_types.append(chart.get("viz_type", "unknown"))
        
        return chart_types
```

### 2-2. テンプレート候補の自動抽出

```python
def extract_template_from_candidates(
    analyzer: ChartUsageAnalyzer,
    candidate: Dict
) -> Dict:
    """テンプレート候補からテンプレートを作成"""
    # サンプルチャートからテンプレートを作成
    sample_chart_id = candidate["sample_chart_ids"][0]
    
    # チャートをエクスポート
    response = requests.get(
        f"{SUPERSET_URL}/api/v1/chart/export/?q=(ids:!({sample_chart_id}))",
        headers=headers
    )
    response.raise_for_status()
    
    template = response.json()
    
    # テナント固有の情報を削除
    template = clean_template(template)
    
    return template

def clean_template(template: Dict) -> Dict:
    """テンプレートからテナント固有の情報を削除"""
    # IDを削除
    if "id" in template:
        del template["id"]
    
    # オーナー情報を削除
    if "owners" in template:
        del template["owners"]
    
    # 作成日時を削除
    if "created_on" in template:
        del template["created_on"]
    if "changed_on" in template:
        del template["changed_on"]
    
    # データソースIDをプレースホルダーに置き換え
    if "datasource_id" in template:
        template["datasource_id"] = "{{DATASOURCE_ID}}"
    
    return template
```

### 2-3. 定期分析の実行

```python
# 定期実行（例: 週次）
def weekly_template_analysis():
    """週次でテンプレート分析を実行"""
    analyzer = ChartUsageAnalyzer(SUPERSET_URL, ADMIN_TOKEN)
    
    # チャート分析
    chart_analysis = analyzer.analyze_chart_usage(days=30, min_usage_count=3)
    
    # ダッシュボード分析
    dashboard_analysis = analyzer.analyze_dashboard_usage(days=30, min_usage_count=2)
    
    # テンプレート候補をレポート
    report_template_candidates(chart_analysis, dashboard_analysis)
    
    # 自動的にテンプレート化（オプション）
    # auto_create_templates(chart_analysis["template_candidates"])

# Cloud SchedulerやCronで定期実行
# 例: 毎週月曜日の午前3時に実行
```

---

## 3. テンプレートの保護

### 3-1. テンプレートフラグの追加

#### データベーススキーマ

```sql
-- チャートにテンプレートフラグを追加
ALTER TABLE slices ADD COLUMN is_template BOOLEAN DEFAULT FALSE;
ALTER TABLE slices ADD COLUMN template_source_id INTEGER;  -- 元のテンプレートID

-- ダッシュボードにテンプレートフラグを追加
ALTER TABLE dashboards ADD COLUMN is_template BOOLEAN DEFAULT FALSE;
ALTER TABLE dashboards ADD COLUMN template_source_id INTEGER;  -- 元のテンプレートID
ALTER TABLE dashboards ADD COLUMN is_protected BOOLEAN DEFAULT FALSE;  -- 保護フラグ
```

#### モデルの拡張

```python
# superset/models/slice.py に追加
class Slice(Model):
    # ... 既存のフィールド
    is_template = Column(Boolean, default=False)
    template_source_id = Column(Integer, ForeignKey("slices.id"), nullable=True)

# superset/models/dashboard.py に追加
class Dashboard(Model):
    # ... 既存のフィールド
    is_template = Column(Boolean, default=False)
    template_source_id = Column(Integer, ForeignKey("dashboards.id"), nullable=True)
    is_protected = Column(Boolean, default=False)  # テンプレートから作成されたものは保護
```

### 3-2. 権限管理の実装

#### カスタムセキュリティマネージャー

```python
from superset.security.manager import SupersetSecurityManager
from superset.exceptions import SupersetSecurityException

class CustomSecurityManager(SupersetSecurityManager):
    def can_write_chart(self, chart: Slice) -> bool:
        """チャートの編集権限をチェック"""
        # テンプレートチャートは編集不可
        if chart.is_template:
            raise SupersetSecurityException(
                "Template charts cannot be modified. Please create a copy first."
            )
        
        # 保護されたチャート（テンプレートから作成されたもの）は編集不可
        if chart.template_source_id is not None:
            # ただし、オーナーは編集可能（オプション）
            if not self.is_owner(chart) and not self.is_admin():
                raise SupersetSecurityException(
                    "This chart is protected. Please create a copy to modify."
                )
        
        return super().can_write_chart(chart)
    
    def can_delete_chart(self, chart: Slice) -> bool:
        """チャートの削除権限をチェック"""
        # テンプレートチャートは削除不可
        if chart.is_template:
            raise SupersetSecurityException(
                "Template charts cannot be deleted."
            )
        
        # 保護されたチャートは削除不可（オプション）
        if chart.template_source_id is not None:
            if not self.is_admin():
                raise SupersetSecurityException(
                    "This chart is protected. Only admins can delete it."
                )
        
        return super().can_delete_chart(chart)
    
    def can_write_dashboard(self, dashboard: Dashboard) -> bool:
        """ダッシュボードの編集権限をチェック"""
        # テンプレートダッシュボードは編集不可
        if dashboard.is_template:
            raise SupersetSecurityException(
                "Template dashboards cannot be modified."
            )
        
        # 保護されたダッシュボードは編集不可
        if dashboard.is_protected:
            if not self.is_admin():
                raise SupersetSecurityException(
                    "This dashboard is protected. Please create a copy to modify."
                )
        
        return super().can_write_dashboard(dashboard)
    
    def can_delete_dashboard(self, dashboard: Dashboard) -> bool:
        """ダッシュボードの削除権限をチェック"""
        # テンプレートダッシュボードは削除不可
        if dashboard.is_template:
            raise SupersetSecurityException(
                "Template dashboards cannot be deleted."
            )
        
        # 保護されたダッシュボードは削除不可
        if dashboard.is_protected:
            if not self.is_admin():
                raise SupersetSecurityException(
                    "This dashboard is protected. Only admins can delete it."
                )
        
        return super().can_delete_dashboard(dashboard)
    
    def can_create_dashboard(self) -> bool:
        """ダッシュボードの作成権限をチェック"""
        # テナントユーザーはダッシュボード作成を制限（オプション）
        user_roles = [role.name for role in self.get_user_roles()]
        
        # Admin、Alphaロールは作成可能
        if "Admin" in user_roles or "Alpha" in user_roles:
            return True
        
        # テナントユーザー（customer_*_admin）は作成不可
        if any(role.startswith("customer_") for role in user_roles):
            raise SupersetSecurityException(
                "Dashboard creation is restricted. Please contact your administrator."
            )
        
        return super().can_create_dashboard()
```

### 3-3. プロビジョニング時の保護フラグ設定

```python
def create_dashboards_from_templates(
    self,
    tenant_id: str,
    database_id: int,
    dataset_ids: Dict[str, int],
    user_id: int
) -> List[int]:
    """テンプレートからダッシュボードを作成（保護フラグを設定）"""
    # ... 既存のコード ...
    
    # インポート後に保護フラグを設定
    for dashboard_id in dashboard_ids:
        self.set_dashboard_protected(dashboard_id, protected=True)
    
    return dashboard_ids

def set_dashboard_protected(self, dashboard_id: int, protected: bool):
    """ダッシュボードの保護フラグを設定"""
    # 直接SQLで更新（APIにフラグがない場合）
    # または、カスタムAPIエンドポイントを作成
    pass
```

### 3-4. チャート作成の制限

#### ロールベースの制限

```python
# テナントユーザーのロール設定
tenant_roles = {
    "customer_a_admin": {
        "permissions": [
            # チャート作成は可能
            "can_write:Chart",
            "can_add:Chart",
            # ダッシュボード作成は不可
            # "can_write:Dashboard",  # コメントアウト
            # "can_add:Dashboard",    # コメントアウト
            # ダッシュボード閲覧は可能
            "can_read:Dashboard",
        ]
    }
}
```

### 3-5. UIでの表示制御

#### フロントエンドでの制限

```typescript
// ダッシュボード作成ボタンを非表示
const canCreateDashboard = (user: User) => {
  const roles = user.roles || {};
  // Admin、Alphaロールのみ表示
  return roles.Admin || roles.Alpha;
};

// 保護されたチャート・ダッシュボードの編集ボタンを非表示
const canEditChart = (chart: Chart) => {
  if (chart.is_template) return false;
  if (chart.template_source_id && !isAdmin()) return false;
  return true;
};
```

---

## 4. 実装のまとめ

### 4-1. テンプレート化のための分析

1. **定期分析の実行**
   - 週次でチャート・ダッシュボードの使用状況を分析
   - よく使われているパターンを抽出
   - テンプレート候補をレポート

2. **テンプレート候補の抽出**
   - 使用回数が閾値以上のチャート・ダッシュボードを抽出
   - パラメータパターンを分析
   - テンプレートとして保存

### 4-2. テンプレートの保護

1. **テンプレートフラグの追加**
   - `is_template`: テンプレートかどうか
   - `template_source_id`: 元のテンプレートID
   - `is_protected`: 保護フラグ

2. **権限管理**
   - テンプレートチャート・ダッシュボードは編集・削除不可
   - 保護されたチャート・ダッシュボードは編集・削除を制限
   - テナントユーザーはダッシュボード作成を制限

3. **UI制御**
   - 編集・削除ボタンを非表示
   - ダッシュボード作成ボタンを非表示

### 4-3. 推奨実装順序

1. **フェーズ1**: テンプレートフラグの追加（データベーススキーマ）
2. **フェーズ2**: 権限管理の実装（カスタムセキュリティマネージャー）
3. **フェーズ3**: プロビジョニング時の保護フラグ設定
4. **フェーズ4**: 使用状況分析の実装
5. **フェーズ5**: 定期分析の自動化

---

## 5. 注意事項

### 5-1. パフォーマンス

- 大量のチャート・ダッシュボードがある場合、分析に時間がかかる可能性
- バッチ処理や非同期処理を検討

### 5-2. プライバシー

- お客さんのデータを分析する際は、プライバシーポリシーに準拠
- テナント間でデータが漏洩しないよう注意

### 5-3. 柔軟性

- 保護フラグは必要に応じて解除可能にする
- Adminユーザーは常に編集・削除可能

