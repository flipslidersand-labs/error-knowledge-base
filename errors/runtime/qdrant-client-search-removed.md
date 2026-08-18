---
title: "qdrant-client 1.18 で client.search() が廃止"
tags: [runtime]
severity: medium
source: personal
---

# qdrant-client 1.18 で client.search() が廃止

**日付**: 2026-06-29
**カテゴリ**: Runtime / API変更

## エラー

```
AttributeError: 'QdrantClient' object has no attribute 'search'
```

## 原因

qdrant-client >= 1.18 で `client.search()` が廃止。

## 修正

```python
# 旧 (1.17以下)
results = client.search(collection_name=col, query_vector=vec, limit=n)

# 新 (1.18+)
response = client.query_points(collection_name=col, query=vec, limit=n)
results = response.points  # .score / .payload を持つ
```

## 関連

- scripts/ingest/qdrant.py の search() 関数
- qdrant サーバ: 1.18.2 (MINIPC <internal-host>:6333)
