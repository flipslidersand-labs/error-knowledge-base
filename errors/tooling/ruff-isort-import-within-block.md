---
title: "ruff I001: from import ブロック内の名前順序違反"
tags: [ruff, isort, python, ci]
severity: low
source: personal
date: "2026-08-10"
---

## 症状

CI の lint ステップ（`ruff check`）が以下で失敗:

```
tests/test_jobs.py:11:1: I001 Import block is un-sorted or un-formatted
```

`from academic_paper.db import (...)` ブロック内で `upsert_job` を `update_paper_status` より前に書いた。

## 原因

ruff の `I` ルール（isort 準拠）は `from X import (a, b, c)` ブロック内の名前も**アルファベット順**を要求する。

`u` で始まる2名前の比較:

- `update_paper_status` → `u-p-d...`
- `upsert_job` → `u-p-s...`

`'d' < 's'` なので `update_paper_status` が先でなければならない。

## 解決策

```python
# NG
from academic_paper.db import (
    upsert_job,
    update_paper_status,  # 'd' < 's' なので後に来てはいけない
)

# OK
from academic_paper.db import (
    update_paper_status,
    upsert_job,
)
```

## 予防

- 複数関数を `from X import (...)` でまとめる際は常にアルファベット順に並べる
- ローカルで `ruff check --fix` を実行してから push すると自動修正される
- 同じ頭文字の名前が混在する場合は2〜3文字目まで比較する習慣をつける
