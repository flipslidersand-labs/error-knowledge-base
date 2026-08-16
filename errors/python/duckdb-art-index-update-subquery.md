---
title: "DuckDB 1.5.x — ART index バグ: UPDATE with subquery fails"
tags: [python]
severity: medium
source: personal
---

# DuckDB 1.5.x — ART index バグ: UPDATE with subquery fails

## 現象

```
_duckdb.FatalException: FATAL Error: Invalid Input Error: Failed to delete all rows from index.
Only deleted 265 out of 280 rows.
```

`UPDATE chunks SET approved=1 WHERE id IN (SELECT ... JOIN ...)` が、
二次インデックス付きテーブルで失敗する。

## 発生条件

- DuckDB 1.5.4
- `CREATE INDEX` が存在するテーブルへの `UPDATE ... WHERE id IN (subquery with JOIN)`

## 回避策

UPDATE 前にインデックスを一時削除し、UPDATE 後に再作成する。

```python
conn.execute("DROP INDEX IF EXISTS idx_chunks_approved")
conn.execute("DROP INDEX IF EXISTS idx_chunks_page")
conn.execute("UPDATE chunks SET approved=1 WHERE id IN (...)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_page ON chunks(page_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_approved ON chunks(approved)")
conn.execute("CHECKPOINT")
```

## 参考

- 発生箇所: `scripts/knowledge.py` の `_update_approval()`
- 修正コミット: `40e2e3b` (feat/phase4-khr-integration)
