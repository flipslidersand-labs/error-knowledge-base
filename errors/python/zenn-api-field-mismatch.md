---
title: "Zenn API フィールド名の罠"
tags: [python]
severity: medium
source: personal
date: "2026-07-01"
---

# Zenn API フィールド名の罠

## 症状

- 記事一覧エンドポイント (`/api/articles`) の `bookmarked_count` を `bookmarks_count` と誤って参照し、常に 0 になった
- `topics` フィールドが記事一覧には含まれず、個別エンドポイント (`/api/articles/<slug>`) にのみ存在する

## 正しい仕様

| フィールド         | 一覧 API | 個別 API |
| ------------------ | -------- | -------- |
| `liked_count`      | ✅       | ✅       |
| `bookmarked_count` | ✅       | ✅       |
| `topics`           | ❌ なし  | ✅ あり  |
| `body_html`        | ❌ なし  | ✅ あり  |

## 対策

- topics・本文が必要な場合は `--body` フラグで個別 API を叩く
- upsert 時に `article.get("bookmarked_count", 0)` を使用する
