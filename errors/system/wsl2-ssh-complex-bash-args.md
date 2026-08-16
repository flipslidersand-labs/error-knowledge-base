---
title: "WSL2 SSH 経由の bash -c 複雑引数が exit 1 で失敗"
tags: [wsl2, ssh, docker, bash]
severity: high
source: personal
date: "2026-08-03"
---

## 症状

```bash
ssh yuki-private "wsl -e bash -c 'docker run -e \"KEY=val\" ...'"
```

複雑な引数（ダブルクォート + 変数展開の混在）を含む場合、SSH + WSL2 経由で `bash -c` を実行すると exit code 1 で失敗する。エラーメッセージなし。

## 原因

SSH → Windows → WSL2 のシェル多段エスケープで引数が壊れる。`-e "KEY=val"` の内側クォートが剥がれて `bash -c` に渡る文字列が解釈不能になる。

## 解決策

スクリプトをファイルとして書き込んでから実行する。

```bash
# 1. stdin 経由でスクリプトをファイルに書き込む
cat << 'SCRIPT' | ssh yuki-private "wsl -e bash -c 'cat > /tmp/run.sh'"
#!/bin/bash
docker run -d \
  -e KEY=val \
  ...
SCRIPT

# 2. スクリプトを実行
ssh yuki-private "wsl -e bash /tmp/run.sh"
```

## 予防

WSL2 SSH 経由では、複数のクォートが必要な場合は `bash -c '...'` を避けてスクリプトファイル経由にする。
