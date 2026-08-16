---
title: "Qdrant memory-ingest が ruri-base tokenizer エラーで失敗する"
tags: [python]
severity: medium
source: personal
date: "2026-07-01"
---

# Qdrant memory-ingest が ruri-base tokenizer エラーで失敗する

## 症状

```
{"status": "error", "message": "Unrecognized processing class in cl-nagoya/ruri-base.
Can't instantiate a processor, a tokenizer ..."}
```

## 原因

`cl-nagoya/ruri-base` モデルの tokenizer config が HuggingFace transformers の
`AutoTokenizer` で認識できないクラスを持っている。
transformers バージョンと ruri-base の tokenizer_config.json の `tokenizer_class` が
不一致の可能性。

## 影響範囲

`scripts/memory-ingest.py` の全 ingest コマンドが失敗する（sessions / facts とも）。

## 未解決・次回確認事項

- transformers バージョン確認 `pip show transformers`
- ruri-base の tokenizer_config.json を確認し `tokenizer_class` の値を調べる
- `sentence-transformers` の別モデル（all-mpnet-base-v2）への切り替えを検討
