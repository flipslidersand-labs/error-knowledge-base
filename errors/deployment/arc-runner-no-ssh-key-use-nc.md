---
title: "ARC runner pod 内で SSH が使えない — nc でポート疎通確認に置き換える"
tags: [arc, github-actions, kubernetes, ssh, nc]
severity: medium
source: personal
date: "2026-08-05"
---

## 症状

`.github/workflows/_wol-ds1.yml` の WoL ワークフローで、
DS1 がオンラインになったか確認するために `ssh` を使っていたが、
ARC runner pod 内に秘密鍵が存在しないため接続に失敗する。

```
ssh: connect to host <internal-host> port 22: Connection refused
Permission denied (publickey)
```

## 原因

ARC (Actions Runner Controller) の runner pod は Kubernetes Pod として起動する。
Pod 内には `~/.ssh/id_*` 等の SSH 鍵が存在しない（マウントしていない）。
SSH 接続の認証フェーズに到達できず、ホストの死活確認自体ができない。

## 解決策

SSH の代わりに `nc`（netcat）でポート疎通確認に置き換える:

```bash
# Before (SSH — ARC pod 内では不可)
ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no user@<internal-host> "exit" 2>/dev/null

# After (nc — TCP 到達チェックのみ)
nc -z -w3 <internal-host> 22
```

`-z`: ポートスキャンモード（データ送受信なし）
`-w3`: タイムアウト 3 秒

## 予防

- ARC runner pod で SSH を使う場合は、Kubernetes Secret + volumeMount で鍵を注入する必要がある
- ホスト死活確認だけが目的なら `nc -z` で十分
- `curl -s --connect-timeout 3 http://IP:PORT/` も代替として使える（HTTPサービスの場合）
