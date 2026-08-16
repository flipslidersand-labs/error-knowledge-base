---
title: "Ollama HTTP 404: cli.py の --model デフォルトが Anthropic モデル名だった"
tags: [python, ollama, doc-ingest, cli]
severity: medium
source: personal
date: "2026-08-16"
---

# Ollama HTTP 404: --model デフォルトが Anthropic モデル名

## 症状

`pnpm doc:ingest <url>` 実行時に Ollama から HTTP 404 が返り蒸留が失敗。

```
POST http://192.168.68.56:11435/api/chat → 404
model "claude-haiku-4-5-20251001" not found
```

## 原因

`scripts/doc_ingest/cli.py` の `--model` 引数のデフォルト値が
`"claude-haiku-4-5-20251001"` になっており、Ollama に存在しないモデル名が渡されていた。

## 解決策

`cli.py` の `--model` デフォルトを `None` に変更。

```python
parser.add_argument(
    "--model",
    default=None,
    help="Anthropic model for fallback (Ollama model is set via OLLAMA_MODEL env)",
)
```

`OLLAMA_MODEL` 環境変数（例: `qwen2.5:7b`）が Ollama 側のモデル選択に使われる。

## 予防

- Ollama と Anthropic で異なるモデル名体系であることを意識する
- `--model` は Anthropic フォールバック専用とし、Ollama 側は env var で制御する設計を維持
