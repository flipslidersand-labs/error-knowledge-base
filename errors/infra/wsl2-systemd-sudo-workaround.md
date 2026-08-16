---
title: "WSL2 で sudo パスワード不要で systemd サービスを登録する方法"
tags: [infra]
severity: medium
source: personal
---

# WSL2 で sudo パスワード不要で systemd サービスを登録する方法

## 発生日

2026-08-02

## 症状

SSH 経由の非インタラクティブセッションでは `sudo` がパスワードを要求し、
systemd サービスファイルの書き込み・登録ができない。

```
sudo: a password is required
```

## 解決策

`wsl -u root` を使って root ユーザーとして直接コマンドを実行する。
WSL2 では `-u root` フラグで sudo なしに root シェルが起動できる。

```bash
ssh yuki-private "wsl -d Ubuntu -u root bash -c '
cat > /etc/systemd/system/myservice.service << SVCEOF
[Unit]
Description=My Service
After=network-online.target

[Service]
Type=simple
User=yukih-linux
ExecStart=/path/to/run.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
SVCEOF
systemctl daemon-reload
systemctl enable --now myservice.service
'"
```

## 前提

- Windows ホスト上で `wsl -u root` が許可されている（デフォルトで許可）
- WSL2 の `/etc/wsl.conf` に `systemd=true` が設定済み

## 注意

heredoc 内でシェル変数展開が必要な場合は `'SVCEOF'` ではなく `SVCEOF`（クォートなし）を使う。
ただし SSH コマンドのクォートと混在するとエスケープが複雑になるため、
内容はファイルで管理して `cat < /path/to/file | tee /etc/systemd/system/...` 経由にするのが安全。

## 関連

- Issue #329: arc-dev-pc-yuki systemd 永続化
