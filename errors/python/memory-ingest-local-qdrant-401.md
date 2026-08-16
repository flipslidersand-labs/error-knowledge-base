---
title: "memory-ingest ローカル Qdrant で 401 Unauthorized"
tags: [qdrant, memory-ingest, api-key]
severity: medium
source: personal
date: "2026-07-28"
---

## 症状

`python3 scripts/memory-ingest.py search --type facts --query "..."` が
`{"status": "error", "message": "Unexpected Response: 401 (Unauthorized)"}` を返す。

## 原因

`_ingest_local()` 内で `os.environ.pop("QDRANT_API_KEY", None)` を呼んでいた。
ローカル Qdrant（localhost:6333）も API キー認証を要求するため、キーを削除すると 401 になる。

## 解決策

`os.environ.pop("QDRANT_API_KEY", None)` 行を削除するだけ。
`~/.config/memory-ingest/env` に設定済みの `QDRANT_API_KEY` がそのまま使われる。

## 予防

ローカル Qdrant を起動する際に `--api-key` オプションを省略しても認証なしにはならない。
Docker Compose の設定で `QDRANT__SERVICE__API_KEY` が設定されていれば認証は必須。
`_ingest_local()` を変更する際は API キーを消さないこと。
