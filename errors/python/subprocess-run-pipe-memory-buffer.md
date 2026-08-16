---
title: "subprocess.run(stdout=PIPE) で大量出力をメモリバッファして肥大化"
tags: [python, subprocess, memory]
severity: medium
source: personal
date: "2026-07-09"
---

## 症状

Rust クローラーの出力を Python で受け取る処理で、`subprocess.run(stdout=PIPE)` を使ったところ
クローラー終了まで全 JSONL 出力がメモリに蓄積し、1.6GB → 3GB 超まで膨れた。
DuckDB への書き込みもその後まとめて行うため、ピーク時は DB 処理とバッファが共存した。

## 原因

```python
# ❌ 悪いパターン
proc = subprocess.run(
    [str(RUST_CRAWLER), "--file", tmp, "--workers", str(workers)],
    stdout=subprocess.PIPE,   # 全出力を subprocess.CompletedProcess.stdout に蓄積
    text=True,
)
# ← ここで初めて1行ずつ処理
for line in proc.stdout.splitlines():
    d = json.loads(line)
    _write_pages_to_db([(d["url"], d["title"], d["text"])], ...)
```

`subprocess.run` はプロセス終了まで全 stdout をバッファに保持する。
クローラーが 19 ページ分の JSONL を出力し終わるまで、その全データが Python プロセスメモリに乗り続ける。

## 解決策

`subprocess.Popen` + `proc.stdout` イテレーションで1行ずつストリーム処理：

```python
# ✅ 正しいパターン
proc = subprocess.Popen(
    [str(RUST_CRAWLER), "--file", tmp, "--workers", str(workers)],
    stdout=subprocess.PIPE,
    stderr=None,   # stderr は subprocess から直接端末へ
    text=True,
    bufsize=1,     # 行バッファリング
)
for line in proc.stdout:           # 1行ずつ受け取り → 即 DB 書き込み
    d = json.loads(line.strip())
    text = d.get("text") or ""
    if len(text) > MAX_TEXT_CHARS:
        text = text[:MAX_TEXT_CHARS]   # 巨大ページのトリムも忘れずに
    _write_pages_to_db([(d["url"], d["title"], text)], ..., conn=conn)
proc.wait()
```

DB 接続を1つ共有して行ごとに使い回す（`conn=conn` を渡す）ことで、接続オーバーヘッドも削減。

## 予防

- 外部プロセスの出力量が事前に分からない場合は `subprocess.Popen` + イテレーション
- `subprocess.run(stdout=PIPE)` はログ収集など「小さい出力が確実」な用途に限定する
- 1 ページあたりのテキスト上限（`MAX_TEXT_CHARS`）を設けてサイズ爆発を防ぐ
