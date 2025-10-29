# FF_Manager（データ管理・分析アプリケーション）
> 🇬🇧 For English version, see [README.md](README.md)

## 目次
- [概要](#概要)
- [開発目的](#開発目的)
- [主な機能](#主な機能)
- [アーキテクチャ](#アーキテクチャ)
- [動作環境](#動作環境)
- [セットアップ](#セットアップ)
- [実行方法](#実行方法)


## 概要

本アプリケーションは、商品の複雑な数値データを効率的に管理・可視化・分析するためのデスクトップアプリケーションです。  
独自のUIを備え、手動入力およびOCRによる画像データの自動取り込みに対応しています。

---

## 開発目的

以下のような課題を解決するために開発を行いました。

- 売上の向上  
- 廃棄ロスの削減  
- 従来の商品データ管理ソフトの可読性が低い  
- データの共有が紙媒体に制限されている

---

## 主な機能

- データ入力機能（手動＋OCR画像読み取り）
- データベースによる保存・検索
- 数値・グラフの可視化（matplotlib）
- 画像からのテーブル自動認識（PaddleOCR）
- マルチタブUIによる画面遷移（PySide6）

---

## アーキテクチャ

- 環境：poetry
- UIフレームワーク：PySide6            
- OCR：PaddleOCR,OpenCV
- DB：SQLite3 
- ライブラリ：numpy,pandas,matplotlib

---

## 動作環境

- python：^>=3.12, <3.14
- poetry：^2.1.4
- pyside6：^6.9.2
- sqlite3：^3.45.3
- windows 10 Home：^2009
---

## セットアップ

1. GitHubからリポジトリを取得
```bash
git clone https://github.com/rookie-2525/FF-Manager-public-.git
cd FF-Manager-public-
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
```
---

## 実行方法
- 通常起動
```bash
poetry env use 3.12
poetry install
poetry run python ff-manager
```
