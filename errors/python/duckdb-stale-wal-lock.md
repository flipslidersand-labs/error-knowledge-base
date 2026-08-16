---
title: "DuckDB WAL stale lock — プロセス強制終了後に IO Error"
tags: [duckdb, python, lock, wal]
severity: medium
source: personal
---

# DuckDB WAL stale lock — プロセス強制終了後に IO Error

## 症状

```
_duckdb.IOException: IO Error: Could not set lock on file "knowledge.duckdb":
Conflicting lock is held in /usr/bin/python3.12 (PID XXXXX) by user dev-nodee.
```

PID を確認すると存在しない（または別プロセス）なのにロックが解除されない。

## 原因

DuckDB を書き込み中に `kill` でプロセスを強制終了すると：

1. WAL ファイル (`knowledge.duckdb.wal`) が残る
2. DB ファイルヘッダーにロックを取った PID が記録される
3. 次回オープン時、その PID が生きているか確認し、生きていれば拒否する
4. （稀に）stale な PID が別のプロセスに再利用されていると永続的にブロックされる

## 解決方法

```bash
# 1. WAL を削除（未コミットの書き込みは失われるが、クロールなら再実行可能）
rm scripts/knowledge.duckdb.wal

# 2. 再オープン（DuckDB が自動回復）
python3 scripts/knowledge.py stats
```

## 予防策

- `kill` ではなく `Ctrl+C`（SIGINT）でプロセスを終了する
- DuckDB 側に memory_limit を設定し OOM kill を避ける
- `get_db()` に `SET memory_limit='1GB'` を設定済み（2026-07-09 対応）

## 関連

- knowledge.py の `get_db()` に `SET memory_limit='1GB'` / `SET threads=2` 追加
