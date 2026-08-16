---
title: "メモリ爆食いプロセスの特定・kill 手順"
tags: [infra]
severity: medium
source: personal
---

# メモリ爆食いプロセスの特定・kill 手順

## 症状

- システムがフリーズ / 応答遅延
- `free -h` で used が急増

## 手順

### 1. メモリ使用量ランキング確認

```bash
ps aux --sort=-%mem | head -10
```

`%MEM` 列が高いプロセスを確認する。

### 2. 何をしているか確認

```bash
cat /proc/<PID>/cmdline | tr '\0' ' '
# または
ps aux | grep <PID>
```

コマンドライン引数がまるごと確認できる。

### 3. kill

```bash
kill <PID>        # 通常終了（SIGTERM）
kill -9 <PID>     # 強制終了（SIGKILL）— 応答しない場合
```

### 4. リアルタイム監視

```bash
htop   # M キーでメモリ順ソート
```

## 実例（2026-07-08）

`scripts/knowledge.py crawl --workers 4` がメモリ 11.5GB + CPU 100% で爆走。
クラッシュダンプ (`erl_crash.dump`) がプロジェクトルートに生成されていた。
原因: クローラーのメモリリーク。`--workers` を減らすか、バッチ処理に組み直す必要あり。
