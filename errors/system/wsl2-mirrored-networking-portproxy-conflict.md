---
title: "WSL2 mirrored networking で portproxy を使うと connection reset になる"
tags: [wsl2, networking, portproxy, node_exporter]
severity: high
source: personal
date: "2026-08-05"
---

## 症状

WSL2 mirrored networking (`networkingMode=mirrored`) 環境で `netsh interface portproxy` を
設定すると、以下の問題が発生する。

1. **"address already in use"**: portproxy が LAN IP:9100 でリッスンしており、
   WSL2 内の node_exporter が同じポートをバインドできない（mirrored networking により
   Windows と WSL2 は同一 IP を共有するため）
2. **"connection reset"**: portproxy が TCP 接続を受け入れるが、
   WSL2 へのデータ転送で接続が切断される（原因不明だが再現性あり）
3. **"empty reply"**: `listenaddress=0.0.0.0` で portproxy を設定すると
   127.0.0.1:PORT 自身にループバックして空レスポンスになる

## 原因

WSL2 mirrored networking は Windows と WSL2 が同一 LAN IP を共有する。
この状態で portproxy を追加しても冗長どころか干渉する。
portproxy は NAT モード用の仕組みであり、mirrored では不要かつ有害。

## 解決策

portproxy を完全削除する:

```powershell
# 管理者 PowerShell
netsh interface portproxy delete v4tov4 listenaddress=192.168.68.60 listenport=9100
# または全削除
netsh interface portproxy reset
```

WSL2 内のサービス（node_exporter 等）はポート 9100 で直接起動すれば、
Windows Firewall を開放するだけで LAN から到達できる:

```powershell
netsh advfirewall firewall add rule name=node_exporter dir=in action=allow protocol=TCP localport=9100
```

## 予防

- mirrored networking 環境では portproxy を新規設定しない
- 既存の portproxy 設定がある場合は `netsh interface portproxy show all` で確認し、
  mirrored 環境では不要なエントリを削除する
- Ollama 用の portproxy は歴史的に残っているが冗長（害はない模様）
