---
title: "jina-embeddings-v2-base-code が transformers 5.x で ImportError"
tags: [python]
severity: medium
source: personal
---

# jina-embeddings-v2-base-code が transformers 5.x で ImportError

## 症状

```
ImportError: cannot import name 'find_pruneable_heads_and_indices' from 'transformers.pytorch_utils'
```

または

```
ValueError: Specified `attn_implementation="torch"` is not supported.
```

## 環境

- `transformers >= 5.0` (確認: 5.12.1)
- `sentence-transformers >= 5.0`
- `jinaai/jina-embeddings-v2-base-code`

## 原因

jina-v2 の custom code (`modeling_bert.py`) が `transformers.pytorch_utils` から
`find_pruneable_heads_and_indices` をインポートしているが、transformers 5.x で削除された。
また model config に `attn_implementation="torch"` が設定されているが、これも 5.x 非対応。

## 解決策

`microsoft/codebert-base` (768-d) に差し替える。同じ 768-d でコード意味理解に特化。

```python
# Before
"model": "jinaai/jina-embeddings-v2-base-code"

# After
"model": "microsoft/codebert-base"
```

## 試したが効かなかった方法

- `trust_remote_code=True` → find_pruneable_heads_and_indices エラーは残る
- `model_kwargs={'attn_implementation': 'eager'}` → 同上
- `jinaai/jina-embeddings-v3` → `einops` パッケージ不足で別エラー
