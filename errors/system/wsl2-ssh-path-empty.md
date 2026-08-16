---
title: "WSL2 SSH セッションで PATH が空になり sudo/docker 等が見つからない"
tags: [wsl2, ssh, path, windows]
severity: medium
source: personal
date: "2026-08-03"
---

## 症状

Windows OpenSSH 経由で WSL2 に接続し `bash -c 'sudo apt-get install ...'` を実行すると以下が出る。

```
The command could not be located because '/bin:/usr/bin' is not included in the PATH environment variable.
sudo: command not found
```

## 原因

`ssh yuki-private "wsl -d Ubuntu -- bash -c '...'"` の形式では `/etc/profile` や `~/.bashrc` が読まれず、PATH が初期化されない。

## 解決策

コマンド冒頭で PATH を明示する。

```bash
ssh yuki-private "wsl -d Ubuntu -- bash -c 'export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin && sudo apt-get install -y docker.io'"
```

またはログインシェルで実行:

```bash
ssh yuki-private "wsl -d Ubuntu -- bash -l -c 'sudo apt-get install -y docker.io'"
```

## 予防

WSL2 へのリモートコマンドは `bash -l` (login shell) を使うか、スクリプト先頭に `export PATH=...` を入れる。
