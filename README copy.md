# FF_Manager (Data Management & Analytics Application)
> 🇯🇵 For Japanese version, see [README_ja.md](README_ja.md)

## Table of Contents
- [Overview](#overview)
- [Purpose](#purpose)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Environment](#environment)
- [Setup](#setup)
- [How to Run](#how-to-run)


## Overview

This desktop application is designed to efficiently manage, visualize, and analyze complex numerical data for products.  
It provides a custom UI and supports both manual entry and automatic ingestion of image data via OCR.

---

## Purpose

Developed to address the following challenges:

- Improving sales  
- Reducing disposal/waste loss  
- Low readability of traditional product data management software  
- Data sharing constrained to paper media

---

## Key Features

- Data entry (manual + OCR image import)
- Persistence & search via database
- Numeric and chart visualization (matplotlib)
- Automatic table detection from images (PaddleOCR)
- Multi-tab UI navigation (PySide6)

---

## Architecture

- Environment: poetry
- UI framework: PySide6            
- OCR: PaddleOCR, OpenCV
- DB: SQLite3 
- Libraries: numpy, pandas, matplotlib

---

## Environment

- python: ^>=3.12, <3.14
- poetry: ^2.1.4
- pyside6: ^6.9.2
- sqlite3: ^3.45.3
- windows 10 Home: ^2009
---

## Setup

1. Get the repository from GitHub
```bash
git clone https://github.com/rookie-2525/FF-Manager-public-.git
cd FF-Manager-public-
```
2. Install Python ^3.12.x  
**If you already have Python (3.12.x to 3.14.x) installed, you can skip this.**  
Install Python 3.12.x from the URL below.  
https://www.python.org/downloads/release/python-3120/?utm_source=chatgpt.com  
Be sure to check “Add Python to PATH” during installation.

3. Install poetry  
**If you already have poetry installed, you can skip this.**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
---

## How to Run
- Normal launch
```bash
poetry env use 3.12
poetry install
poetry run python ff-manager
```
