---
title: "k3s WSL2 インストール が sudo でハング（30+分）"
tags: [wsl2, k3s, sudo, systemd]
severity: high
source: personal
date: "2026-08-13"
---

## 症状

YUKI WSL2 Ubuntu で k3s インストールコマンド実行時に sudo で権限昇格しようとしたが、パスワード入力を求められてハング（50+ 分）。

```bash
ssh yuki-private 'curl -sfL https://get.k3s.io | sudo sh -'
# → パスワード入力待ち → タイムアウト
```

## 原因

WSL2 では systemd が init になっており、sudo を使う場合は **パスワード認証が必須**。
リモート SSH セッションからパスワード入力できず、タイムアウト。

## 解決策

sudo ではなく `wsl -u root` を使って直接 root で実行:

```bash
ssh yuki-private 'wsl -u root bash -c "curl -sfL https://get.k3s.io | sh -"'
```

これにより:

- パスワード入力不要
- WSL Ubuntu 内で root shell で直接実行
- タイムアウトなし

## 予防

WSL2 内での root 実行が必要な場合は `sudo` ではなく `wsl -u root` 経由で行う。
特に CI/CD パイプラインからの自動実行時に有効。
