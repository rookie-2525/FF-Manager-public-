> 🇬🇧 For English version, see [README.md](README.md)
# FF_Manager（データ管理・分析アプリケーション）

## 概要

本アプリケーションは、商品の複雑な数値データを効率的に管理・可視化・分析するためのデスクトップアプリケーションです。  
独自のUIを備え、手動入力およびOCRによる画像データの自動取り込みに対応しています。

---

## 開発目的

以下のような課題を解決するために開発を行いました。

- 売上の向上  
- 廃棄ロスの削減  
- 従来の商品データ管理ソフトの可読性が低かった  
- データの共有が紙媒体に制限されていた  

---

## 主な機能

- データ入力機能（手動＋OCR画像読み取り）
- データベースによる保存・検索
- 数値・グラフの可視化（matplotlib）
- 画像からのテーブル自動認識（PaddleOCR）
- マルチタブUIによる画面遷移（PySide6）

---

## 使用言語・ライブラリ

-カテゴリ-          -技術名-            
----------------:------------------------
エディタ 　　 　 ：Visual Studio Code
言語            ：Python
環境            ：poetry
リポジトリ       :GitHub 
UIライブラリ　　 ：PySide6            
OCR             :PaddleOCR（PP-Structure） 
DB              :SQLite3 
その他          ：Pandas, Ruff, pre-commit など 

---

## 動作環境

- python : ^>=3.12, <3.14
- poetry : ^2.1.4
- pyside6: ^6.9.2
- sqlite3: ^3.45.3
- windows 10 Home ^2009
---

## 実行方法

1. GitHubからリポジトリを取得
```bash
git clone https://github.com/rookie-2525/FFM-repositry.git
cd FFM-repositry
```
2. python ^3.12.xの導入
**すでにpython(3.12.xから3.14.x)を導入済みの方は飛ばしてください**
以下のURLからPython 3.12.x をインストールしてください。
https://www.python.org/downloads/release/python-3120/?utm_source=chatgpt.com
インストール時は必ず「Add Python to PATH」にチェックを入れてください。

3. poetryの導入
**すでにpoetryを導入済みの方は飛ばしてください**
```bash
curl -sSL https://install.python-poetry.org | python3 -
#--------ターミナルを再起動--------#
poetry env use 3.12
poetry install
```
4. スクリプトの実行
```bash
poetry run python src/ff_manager/main.py
```

---

## テストの実行
```bash
poetry run pytest
```
