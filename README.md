# Automated Notion Reporting System

## 概要 (Overview)

このプロジェクトは、ローカルのファイル（`.html`, `.txt`）をデータソースとして自動的に収集・処理し、その結果をNotionデータベースに記録し、HTML形式のダッシュボードを生成する自動化ツールです。処理の進捗状況はSlackにも通知されます。

This project is an automation tool that automatically collects and processes local files (`.html`, `.txt`) as data sources, records the results in a Notion database, and generates an HTML dashboard. The progress of the processing is also notified to Slack.

## 主な機能 (Features)

- **データ収集 (Data Fetching):** `data/` ディレクトリ内のファイルを自動的にスキャンして内容を読み込みます。
- **Notion連携 (Notion Integration):** 実行ごとに、指定されたNotionデータベースに新しい行（ページ）として結果を記録します。
- **Slack通知 (Slack Notifications):** ワークフローの各ステップ（データ取得、Notion更新、ダッシュボード生成）の完了やエラーを、指定されたSlackチャンネルに通知します。
- **HTMLダッシュボード生成 (HTML Dashboard Generation):** 処理したファイルの一覧を含む、見やすいHTML形式のレポートを `dashboard/` ディレクトリに生成します。
- **設定ファイルによる管理 (Configuration-driven):** `config.py` ファイルでNotionやSlackのAPIキー、各種設定を集中管理します。

## プロジェクト構造 (Project Structure)

```
.
├── config.py               # 設定ファイル (APIキーなど)
├── main.py                 # メイン実行スクリプト
├── fetch_data.py           # データ収集モジュール
├── update_notion.py        # Notion更新モジュール
├── slack_notify.py         # Slack通知モジュール
├── generate_dashboard.py   # ダッシュボード生成モジュール
├── requirements.txt        # 依存ライブラリ
├── templates/
│   └── dashboard_template.html # ダッシュボードのHTMLテンプレート
├── data/                   # 処理対象のファイルを置く場所
├── dashboard/              # 生成されたHTMLダッシュボードが保存される場所
└── logs/                   # 実行ログが保存される場所
```

## クイックスタート (Quick Start)

1.  **リポジトリをクローンします。**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **依存関係をインストールします。**
    ```bash
    pip install -r requirements.txt
    ```

3.  **設定ファイルを編集します。**
    - `config.py` を開き、ご自身の `NOTION_TOKEN`, `NOTION_DATABASE_ID`, `SLACK_WEBHOOK_URL` を設定します。

4.  **データファイルを配置します。**
    - `data/` ディレクトリに、処理したい `.html` または `.txt` ファイルを置きます。

5.  **スクリプトを実行します。**
    ```bash
    python main.py
    ```

より詳細な手順については、`USAGE_GUIDE.md` を参照してください。
