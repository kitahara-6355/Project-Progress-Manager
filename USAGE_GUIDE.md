# ユーザー利用ガイド (Usage Guide)

このガイドは、「Automated Notion Reporting System」のセットアップから実行、結果の確認までを、初心者の方でも迷わずに行えるように詳細に説明します。

## 目次 (Table of Contents)
1.  [初回セットアップ (Initial Setup)](#1-初回セットアップ-initial-setup)
2.  [各種サービスの設定 (Configuration)](#2-各種サービスの設定-configuration)
3.  [スクリプトの実行 (Running the Script)](#3-スクリプトの実行-running-the-script)
4.  [実行結果の確認 (Checking the Output)](#4-実行結果の確認-checking-the-output)
5.  [トラブルシューティング (Troubleshooting)](#5-トラブルシューティング-troubleshooting)

---

## 1. 初回セットアップ (Initial Setup)

まず、スクリプトを実行するためのPC環境を準備します。

### 1.1. Pythonのインストール
このスクリプトはPythonで書かれています。PCにPythonがインストールされていない場合は、インストールが必要です。
- **推奨:** [Python公式サイト](https://www.python.org/downloads/windows/)から最新版をダウンロードします。
- **重要:** インストール時に、**「Add Python to PATH」** というチェックボックスに**必ずチェックを入れてください。** これを忘れると、後の手順で `python` コマンドが見つからないエラーが発生します。

### 1.2. プロジェクトファイルの準備
- このプロジェクトのファイルをPCの好きな場所（例: デスクトップ）に配置します。

### 1.3. 必要なライブラリのインストール
プロジェクトフォルダに移動し、ターミナル（コマンドプロンプトやPowerShell）で以下のコマンドを実行して、スクリプトが必要とするライブラリをインストールします。
```bash
pip install -r requirements.txt
```

---

## 2. 各種サービスの設定 (Configuration)

スクリプトがNotionやSlackと連携するために、いくつかのキー情報を取得し、設定ファイルに書き込む必要があります。

### 2.1. Notionの設定
このスクリプトは、実行結果をNotionの**データベース**に記録します。

1.  **データベースの作成:**
    - Notionで、レポートを記録するための新しい**データベース**を作成します（フルページ形式を推奨）。
    - データベースのタイトルは「自動レポート」など、お好きな名前にしてください。
    - **重要:** データベースの列（プロパティ）は、**何も追加・変更する必要はありません。** 新規作成時に自動でできる「**Name**」という名前のタイトル列があれば、それで十分です。

2.  **Notion APIトークンの取得:**
    - [Notionのインテグレーション管理ページ](https://www.notion.so/my-integrations)にアクセスします。
    - 「**New integration**」を作成し、名前を付けます。
    - 作成後、「**Internal Integration Token**」という項目に表示される `secret_...` から始まるトークンをコピーします。

3.  **データベースとインテグレーションの連携:**
    - 作成したNotionデータベースの右上にある「・・・」メニューから、「**Add connections**」を選び、先ほど作成したインテグレーションを選択して連携を許可します。

4.  **データベースIDの取得:**
    - 連携したデータベースをブラウザで開きます。
    - アドレスバーのURL `https://www.notion.so/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx?v=...` の、`so/` の直後にある32文字の英数字が**データベースID**です。これをコピーします。

### 2.2. Slackの設定
1.  **Slack Appの作成:** [Slack APIサイト](https://api.slack.com/apps)にアクセスし、「**Create an App**」→「**From scratch**」で新しいアプリを作成します。
2.  **Incoming Webhooksの有効化:** アプリ管理画面の「**Incoming Webhooks**」メニューで、機能を **On** にします。
3.  **Webhook URLの生成:** ページ下部の「**Add New Webhook to Workspace**」をクリックし、通知を送りたいチャンネルを選択して許可すると、`https://hooks.slack.com/services/...` というURLが生成されます。これをコピーします。

### 2.3. `config.py` ファイルの編集
取得した3つの情報を、プロジェクトフォルダ内の `config.py` ファイルに設定します。

```python
# Notion APIトークンを貼り付け
NOTION_TOKEN = "secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# NotionデータベースIDを貼り付け
NOTION_DATABASE_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Slack Webhook URLを貼り付け
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/xxxx/yyyy/zzzz"
```

---

## 3. スクリプトの実行 (Running the Script)

### 3.1. データファイルの準備
- プロジェクトフォルダ内の `data/` ディレクトリに、処理させたい `.html` や `.txt` ファイルをいくつか置きます。
- このディレクトリが空のままでもスクリプトは動作しますが、レポートには「ファイルが見つかりません」と記録されます。

### 3.2. 実行
ターミナルで、以下のコマンドを実行します。
```bash
python main.py
```
*(もし `python` コマンドでエラーが出る場合は `py main.py` をお試しください)*

---

## 4. 実行結果の確認 (Checking the Output)

スクリプトが正常に完了すると、以下の成果物が生成されます。

- **Notion:** `config.py` で指定したデータベースに、`Data Import - (実行日時)` というタイトルの新しい行（ページ）が追加されます。そのページを開くと、処理されたファイルの一覧が記載されています。
- **HTMLダッシュボード:** `dashboard/` ディレクトリに `index.html` が生成されます。このファイルをブラウザで開くと、見やすいレポートが表示されます。
- **Slack:** `config.py` で指定したチャンネルに、処理の進捗を知らせる通知が届きます。
- **ログファイル:** `logs/` ディレクトリに `app.log` が生成されます。エラーが発生した場合など、詳細な動作の記録がここに保存されます。

---

## 5. トラブルシューティング (Troubleshooting)

- **`ModuleNotFoundError`:** `pip install -r requirements.txt` が正しく実行されていない可能性があります。再度実行してみてください。
- **NotionのAPIエラー:** `config.py` の `NOTION_TOKEN` や `NOTION_DATABASE_ID` が正しいか、インテグレーションの連携が許可されているか、再度ご確認ください。特に、トークンやIDの末尾に**余分なスペース**が入っていないかご注意ください。
- **`python` コマンドが見つからない:** Pythonのインストール時に「Add Python to PATH」にチェックを入れ忘れた可能性があります。`py main.py` を試すか、Pythonを再インストールしてオプションを有効にしてください。
