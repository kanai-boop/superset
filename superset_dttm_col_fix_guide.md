# Superset: `main_dttm_col` 未設定によるエラー解決ガイド

## 1. 概要

本ドキュメントは、Apache Supersetのダッシュボードで時間関連のフィルタやチャートが `Data error: Datetime column not provided` などのエラーで表示されない問題の解決手順を記録するものです。

根本的な原因は、データセットに主要な時間軸カラム (`main_dttm_col`) が設定されていないことでした。ここでは、API経由でこの設定を行うことを最終目標としますが、その過程で発生した開発環境のセットアップに関する様々な問題と、その解決策もあわせて記載します。

## 2. 発生した問題と解決策のタイムライン

APIスクリプトの実行に至るまでに、以下の環境構築に関する問題が発生しました。

### 問題1: Pythonの実行環境エラー

- **事象**: `python` コマンドが存在しない、または `requests` などの必須ライブラリがインストールされていない。
- **原因**:
    1.  システムのデフォルト `python` が `python3` であった。
    2.  プロジェクト用のPython仮想環境が有効になっていなかった。
- **解決策**:
    - `python3` を使用する。
    - プロジェクトのドキュメント (`development.mdx`) に従い、仮想環境を作成・有効化する。

### 問題2: Pythonの依存関係インストール失敗 (`click==8.2.1`)

- **事象**: `pip install -r requirements/development.txt` の実行中、`click==8.2.1` が見つからないというエラーが発生。
- **原因**: `click==8.2.1` は **Python 3.10以上**を要求するが、システムデフォルトの `python3` が **Python 3.9** であったため、互換性のない仮想環境が作成されていた。
- **解決策**:
    1.  Homebrewを使い、`brew install python@3.10` コマンドでPython 3.10をインストール。
    2.  既存のPython 3.9ベースの仮想環境 (`venv` ディレクトリ) を一度削除。
    3.  `python3.10 -m venv venv` コマンドで、Python 3.10ベースの新しい仮想環境を再作成。

### 問題3: Pythonの依存関係インストール失敗 (`mysqlclient`)

- **事象**: 依存関係のインストール中、`mysqlclient` パッケージのビルドに失敗する。
- **原因**: `mysqlclient` のコンパイルに必要なOSレベルのライブラリ (`pkg-config` と MySQL/MariaDB の開発ヘッダファイル) が不足していた。
- **解決策**:
    - Homebrewを使い、`brew install mysql pkg-config` コマンドで不足しているOS依存関係をインストール。

## 3. 確立された解決手順

以上のトラブルシューティングを経て、問題を解決するための完全な手順は以下の通りです。

### ステップ1: OS環境の準備

macOS環境において、Homebrewを使い必要なツールをインストールします。

```bash
# Python 3.10 をインストール
brew install python@3.10

# mysqlclient のビルドに必要なツールをインストール
brew install mysql pkg-config
```

### ステップ2: Python仮想環境の構築

プロジェクトのルートディレクトリで、Python 3.10をベースとした仮想環境を作成し、依存ライブラリをインストールします。

```bash
# 既存の仮想環境があれば削除
rm -rf venv

# Python 3.10 で仮想環境を作成
python3.10 -m venv venv

# 仮想環境を有効化し、全ての開発用ライブラリをインストール
source venv/bin/activate
pip install -r requirements/development.txt
```
*(注意: `pip install` には数分かかることがあります)*

### ステップ3: APIによるデータセットの更新

以下の2つのスクリプトを用意し、作成した仮想環境内で実行します。

#### a) `main_dttm_col` の設定

データセットの `main_dttm_col` を設定します。この際、`PUT` リクエストで他の設定項目が失われないよう、既存の設定値を取得してから更新するのが安全です。

**スクリプト例 (`set_main_dttm_col.py`):**
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from scripts.superset_tools.api_client import SupersetClient

def set_main_dttm_col(dataset_id: int, col_name: str):
    print(f"Attempting to set 'main_dttm_col' to '{col_name}' for dataset {dataset_id}...")
    client = SupersetClient()
    try:
        client.login()
        dataset = client.get_dataset(dataset_id)
        update_payload = {
            "database_id": dataset["database"]["id"],
            "owners": [owner["id"] for owner in dataset["owners"]],
            "schema": dataset.get("schema"),
            "table_name": dataset.get("table_name"),
            "main_dttm_col": col_name,
        }
        result = client.update_dataset(dataset_id, update_payload)
        print(f"Successfully updated dataset {dataset_id}:", result)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    set_main_dttm_col(31, "segments_date")
```

#### b) メタデータのリフレッシュ

データセットのスキーマ情報をSupersetに再同期させます。

**スクリプト例 (`refresh_dataset.py`):**
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from scripts.superset_tools.api_client import SupersetClient

def refresh_dataset_metadata(dataset_id: int):
    print(f"Attempting to refresh metadata for dataset {dataset_id}...")
    client = SupersetClient()
    try:
        client.login()
        result = client.refresh_dataset(dataset_id)
        print(f"Successfully triggered refresh for dataset {dataset_id}:", result)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    refresh_dataset_metadata(31)
```

**実行:**
```bash
source venv/bin/activate
python3 scripts/set_main_dttm_col.py
python3 scripts/refresh_dataset.py
```

### ステップ4: UIでの最終調整

1.  SupersetのUIにログインします。
2.  今回変更したデータセット (この例では ID: 31) を使用している **全てのチャート** を一つずつ開きます (Explore Chart)。
3.  何も変更せず、そのまま **「Save」** ボタンを押してチャートを保存し直します。これにより、チャートが `main_dttm_col` の新しい設定を認識します。
4.  関連するダッシュボードを再読み込みし、エラーが解消されていることを確認します。

---

## 4. API経由での2軸グラフ設定ガイド

`mixed_timeseries` チャートにおいて、API経由で2軸表示（デュアルアクシス）を設定する際の手順と重要なパラメータを記録します。

### 問題点

APIで `use_y_axis_2: true` を設定するだけでは2軸表示が有効にならず、単一のY軸で表示されてしまう。これは、UIが内部で生成する、より詳細なパラメータがAPIリクエストに含まれていないためです。

### 解決策: 詳細な`params`設定

UIで正しく設定されたチャートの `params` を分析した結果、APIで2軸表示を確実に有効化するには、以下のキーを含む詳細な設定オブジェクトを渡す必要があることが判明しました。

#### 必須パラメータ

| キー | 説明 | 設定例 |
| --- | --- | --- |
| `metrics` | Query A（左軸）の指標リスト。 | `['cost']` |
| `metrics_b` | Query B（右軸）の指標リスト。`secondary_metrics` ではない。 | `['roas']` |
| **`yAxisIndex`** | Query Aを割り当てる軸のインデックス。 | `0` |
| **`yAxisIndexB`** | **【最重要】** Query Bを割り当てる軸のインデックス。これを `1` にすることが2軸表示の鍵。 | `1` |
| `seriesType` | Query Aのグラフ種別。 | `'line'` |
| `seriesTypeB` | Query Bのグラフ種別。 | `'line'` |
| `y_axis_format` | 左軸のD3フォーマット。 | `'~s'` （SI単位系） |
| `y_axis_format_secondary` | 右軸のD3フォーマット。`y_axis_2_format` ではない。 | `'.2%'` （パーセント） |

#### スクリプト例

以下のスクリプトは、チャートID `282` を対象に、上記パラメータを網羅した `params` を設定する例です。

```python
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def set_dual_axis_chart(chart_id: int):
    """
    Sets a mixed time-series chart to dual-axis mode with detailed parameters.
    """
    client = SupersetClient()
    client.login()

    print(f"Fetching chart {chart_id} to get base params...")
    chart_data = client.get_chart(chart_id)
    params = json.loads(chart_data.get("params", "{}"))

    print("Constructing a full payload for dual-axis display...")

    # --- Query and Metric assignment ---
    params['metrics'] = ['cost']
    params['metrics_b'] = ['roas'] # Use 'metrics_b'

    # --- Axis Assignment (CRITICAL) ---
    params['yAxisIndex'] = 0
    params['yAxisIndexB'] = 1 # This is the key to enable dual-axis

    # --- Chart Type Assignment ---
    params['seriesType'] = 'line'
    params['seriesTypeB'] = 'line'

    # --- Axis Formatting ---
    params['y_axis_format'] = '~s'
    params['y_axis_format_secondary'] = '.2%' # Use 'y_axis_format_secondary'

    # The 'use_y_axis_2' key is likely not needed when yAxisIndexB is set,
    # but can be included for completeness.
    params['use_y_axis_2'] = True

    payload = {"params": json.dumps(params)}

    print("Updating chart...")
    client.update_chart(chart_id, payload)

    print(f"Chart {chart_id} has been updated for dual-axis display.")

if __name__ == "__main__":
    set_dual_axis_chart(282)
```

このアプローチにより、UIを介さずにAPIだけで安定して2軸グラフを作成できる可能性が高まります。

---

## 5. API経由でのBig Numberチャート比較設定ガイド

`big_number` チャートにおいて、API経由で前期間比較（`Δ%`）を設定し、サブヘッダーのフォントサイズを調整する際の手順と重要なパラメータを記録します。

### 問題点

APIで `time_compare: "previous period"` や `subheader_font_size` を設定するだけでは期待通りに動作しない。これは、UIが内部で生成する、より詳細なパラメータがAPIリクエストに含まれていないためです。

### 解決策: 詳細な`params`設定

UIで正しく設定されたチャートの `params` を分析した結果、APIでBig Numberチャートの比較設定を確実に有効化するには、以下のキーを含む詳細な設定オブジェクトを渡す必要があることが判明しました。

#### 必須パラメータ

| キー | 説明 | 設定例 |
| :--- | :--- | :--- |
| `compare_lag` | **【最重要】** 比較対象とする期間のラグ。`1` は直前の期間を意味する。 | `1` （数値） |
| `comparison_type` | 比較結果の表示形式。`'percentage'` で `Δ%` を表示。 | `'percentage'` |
| `subheader_font_size` | サブヘッダー（比較結果）のフォントサイズ。`0.15` はUIの"small"に相当。 | `0.15` （浮動小数点数） |
| `show_delta` | 比較結果の差異を表示するか。 | `True` |
| `show_percent` | 比較結果をパーセンテージで表示するか。 | `True` |

#### スクリプト例

以下のスクリプトは、Big Numberチャートを対象に、上記パラメータを網羅した `params` を設定する例です。

```python
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def set_bignumber_comparison(chart_id: int):
    """
    Sets a Big Number chart to display comparison to the previous period.
    """
    client = SupersetClient()
    client.login()

    print(f"Fetching chart {chart_id} to get base params...")
    chart_data = client.get_chart(chart_id)
    params = json.loads(chart_data.get("params", "{}"))

    print("Constructing a full payload for Big Number comparison...")

    # --- Comparison Settings (CRITICAL) ---
    params["compare_lag"] = 1 # Compare to the immediately preceding period
    params["comparison_type"] = "percentage" # Show as Delta Percentage (Δ%)
    params["show_delta"] = True # Show the delta value
    params["show_percent"] = True # Show the percentage change

    # --- Subheader Font Size ---
    params["subheader_font_size"] = 0.15 # Corresponds to 'small' in UI

    payload = {"params": json.dumps(params)}

    print("Updating chart...")
    client.update_chart(chart_id, payload)

    print(f"Chart {chart_id} has been updated for comparison display.")

if __name__ == "__main__":
    # Example for one chart, apply to others as needed
    set_bignumber_comparison(276)
```

このアプローチにより、UIを介さずにAPIだけで安定してBig Numberチャートの比較設定を行うことが可能になります。

---

## 6. API経由でのTime Comparison設定ガイド

テーブルチャートなどで「WoW%(前週比)」などの期間比較を表示する`Time Comparison`機能は、API経由で設定する際に注意が必要です。

### 問題点

チャートの`params`内で`time_range`キーに`"Last 90 days"`のような相対的な期間文字列を指定してAPIでチャートを作成すると、チャート表示時に`Error: An enclosed time range (both start and end) must be specified when using a Time Comparison.`というエラーが発生する。

これは、`Time Comparison`機能がバックエンドで具体的な開始日と終了日を要求するのに対し、API経由で渡された相対的な期間文字列が正しく解釈されない（あるいは、具体的な日付に変換されない）ために発生します。

### 解決策: UIフィルターの利用

このエラーを確実に回避し、期間比較を有効にする方法は、チャート内部の`time_range`パラメータに頼るのではなく、**ダッシュボードのUI上で「時間範囲」フィルターを適用する**ことです。

**推奨されるワークフロー:**
1.  **チャート作成時:** APIでチャートを作成する際、`params`内の`time_range`は設定しないか、あるいは`"No filter"`のようにデフォルトの状態にしておきます。`compare_lag`や`comparison_type`など、期間比較自体の設定は行います。
2.  **ダッシュボードでの設定:**
    *   作成したチャートをダッシュボードに追加します。
    *   ダッシュボードの編集画面で「フィルターを追加/編集」を選択し、「時間範囲フィルター」を配置します。
    *   そのフィルターのデフォルト値として「前四半期（Last quarter）」などを設定します。

UI上のフィルターは、クエリ実行時に具体的な開始日・終了日に変換されるため、`Time Comparison`機能の要件を満たすことができます。APIで直接`time_range`を設定しようとすると不安定な挙動になるため、UIでのフィルター適用が現在の最も確実な方法です。

---

## 7. API経由でのデータセット・メトリクス更新ガイド

データセットにAPI経由でメトリクスを追加・更新しようとした際に、`422 UNPROCESSABLE ENTITY` エラーと共に `{'message': {'metrics': ['One or more metrics already exist']}}` というメッセージで失敗することがあります。これは非常に解決が困難な問題です。

### 問題点

このエラーは、以下のような複雑な状況で発生します。

1.  **APIの仕様:** Supersetのデータセット更新API (`PUT /api/v1/dataset/{id}`) は、ペイロードにメトリクスの`id`が含まれていない場合は「新規作成」、`id`が含まれている場合は「上書き更新」として扱います。
2.  **キャッシュ問題:** APIでデータセット情報を取得 (`GET /api/v1/dataset/{id}`) した際に、Supersetの多層的なキャッシュ（Redisやアプリケーションのインメモリキャッシュ）が原因で、古い情報（部分的にしかメトリクスが存在しないなど）が返されることがあります。
3.  **悪循環:**
    *   古い情報に基づいて「存在しないメトリクス」を`id`なしで追加しようとすると、DB上には既に存在するため「既に存在する」エラーで失敗します。
    *   かといって、古い情報しかないので正しい`id`を付けて「上書き更新」することもできません。
    *   キャッシュクリアやコンテナ再起動を試みても、この問題が解消されない場合があります。

### 解決策: 「リセット作戦」

この堂々巡りを断ち切るための最も確実な方法は、一度データセットのメトリクスを完全に空にしてから、改めて全てのメトリクスを「新規作成」として一括登録する「リセット作戦」です。

**推奨されるワークフロー:**

1.  **ステージ1: 全メトリクスの削除**
    *   データセット更新APIに対し、`metrics`を空のリスト `[]` にしたペイロードを送信し、全てのメトリクスを削除します。
2.  **ステージ2: 全メトリクスの新規作成**
    *   直後に、必要とする全てのメトリクスを`id`なしの状態でリストにし、再度データセット更新APIに送信します。これにより、全てのメトリクスがクリーンな状態で新規作成されます。

#### スクリプト例

以下は、この2段階の作戦を実行するためのスクリプト例です。

**ステージ1用スクリプト (`reset_dataset_metrics.py`):**
```python
import json
from superset_tools.api_client import SupersetClient

def reset_dataset_metrics(dataset_id: int):
    """
    Deletes all metrics from a given dataset by overwriting with an empty list.
    """
    client = SupersetClient()
    client.login()

    payload = {"metrics": []}

    print(f"Attempting to delete all metrics from dataset {dataset_id}...")
    try:
        client.update_dataset(dataset_id, payload)
        print(f"Successfully deleted all metrics from dataset {dataset_id}.")
    except Exception as e:
        print(f"Error deleting metrics from dataset {dataset_id}: {e}")

if __name__ == "__main__":
    # 対象のデータセットIDを指定
    DATASET_ID = 34
    reset_dataset_metrics(DATASET_ID)
```

**ステージ2用スクリプト (`set_ga_metrics_directly.py`):**
```python
import json
from superset_tools.api_client import SupersetClient

def set_ga_dataset_metrics(dataset_id: int):
    """
    Sets a predefined list of GA4 metrics to a given dataset,
    overwriting any existing metrics.
    """
    client = SupersetClient()
    client.login()

    # データセットにあるべきメトリクスの完全なリストを定義
    final_metrics_payload = {
        "metrics": [
            {
                "metric_name": "count",
                "verbose_name": "COUNT(*)",
                "expression": "COUNT(*)",
                "metric_type": "count",
                "d3format": ",d",
            },
            # ... ここに他の全てのメトリクス定義を追加 ...
            {
                "metric_name": "Sessions",
                "verbose_name": "Sessions",
                "expression": "COUNT(DISTINCT unique_session_id)",
                "metric_type": "count_distinct",
                "d3format": ",d",
            },
        ]
    }

    print(f"Attempting to overwrite metrics for dataset {dataset_id}...")
    try:
        client.update_dataset(dataset_id, final_metrics_payload)
        print(f"Successfully set metrics on dataset {dataset_id}.")
    except Exception as e:
        print(f"Error updating dataset {dataset_id}: {e}")

if __name__ == "__main__":
    # 対象のデータセットIDを指定
    DATASET_ID = 34
    set_ga_dataset_metrics(DATASET_ID)
```

この「リセット作戦」は、APIの挙動が不安定な場合の最終手段として非常に有効です。