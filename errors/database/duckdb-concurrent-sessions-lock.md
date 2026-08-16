---
title: "DuckDB 複数 Claude セッションが同時書き込みでロック競合"
tags: [duckdb, concurrency, claude-code]
severity: medium
source: personal
date: "2026-07-09"
---

## 症状

複数の Claude Code セッションが同じ `knowledge.duckdb` に同時に書き込もうとし、
全セッションが `IO Error: Could not set lock on file` で失敗し続ける。
セッション A が終わるとセッション B が取得 → C が待つ、という連鎖で永遠に詰まる。

```
_duckdb.IOException: IO Error: Could not set lock on file "scripts/knowledge.duckdb":
Conflicting lock is held in /usr/bin/python3.12 (PID 51678) by user dev-nodee.
```

## 原因

- DuckDB はシングルライター設計（PostgreSQL と異なりマルチプロセス書き込みは非対応）
- Claude Code は複数セッションを並列起動できるため、それぞれが独立して `knowledge.py` を実行
- 各セッションが異なるタグ（rust / go / python）で同時 crawl/push しようとする

## 解決策

### 即時対策

他の Claude セッションが終わるまで待つ（現セッションで以下をポーリング）：

```bash
while kill -0 <PID> 2>/dev/null; do sleep 5; done
```

### 根本対策（未実装）

1. **`knowledge.py` にファイルロック機構を追加** — `fcntl.flock` でプロセスをキューイング
2. **DuckDB を read_only モードで開く** — stats/list は `duckdb.connect(path, read_only=True)` で競合しない
3. **実行を1セッションに限定する** — `tmux` や `at` コマンドで逐次実行をスケジュール

### 緊急時（作業中の別セッションを kill したい場合）

```bash
ps aux | grep "knowledge.py" | grep -v grep | awk '{print $2}'  # PID 確認
kill <PID>  # 必要なら
```

ただし DuckDB ファイルは書き込み中断でも WAL により整合性は保たれる。

## 予防

- `knowledge.py crawl/push` を複数セッションで同時実行しない
- タグ別に実行順序を決めて逐次化する（例: knowledge-cron.sh は1プロセスで全タグをループ）
- `DuckDB` のメモリ制限も忘れずに: `SET memory_limit='1GB'; SET threads=2;`
