---
title: "Windows Firewall が WSL2 Docker ポートをブロック（外部接続不可）"
tags: [wsl2, docker, windows, firewall, networking]
severity: high
source: personal
date: "2026-08-03"
---

## 症状

WSL2 内で Docker コンテナを起動し `-p 9200:9200` でバインドしても、外部（同一 LAN の別ホスト）から接続タイムアウトになる。
`netstat -tlnp` では WSL2 側は LISTEN しているが LAN からは到達できない。

## 原因

WSL2 は mirrored networking モードでも Windows Firewall のインバウンドルールが未定義のポートへの接続をブロックする。
Linux 側の `ufw` / iptables ではなく Windows 側の Firewall が関係する。

## 解決策

Windows 側で inbound ルールを追加する（SSH 経由で実行可）：

```bash
ssh yuki-private "netsh advfirewall firewall add rule name=\"OpenSearch 9200\" dir=in action=allow protocol=TCP localport=9200"
```

複数ポートの場合：

```bash
ssh yuki-private "netsh advfirewall firewall add rule name=\"Qdrant\" dir=in action=allow protocol=TCP localport=6333-6334"
```

## 予防

WSL2 で新しいポートを公開する際は、必ず Windows Firewall inbound ルールを追加する。
`docker run -p` だけでは外部接続は開かない。
