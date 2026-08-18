---
title: "WSL2 k3s pod の TCP 443 ブロック（mirrored networking 時）"
tags: [wsl2, k3s, networking, iptables, pod]
severity: high
source: personal
date: "2026-08-13"
---

## 症状

YUKI WSL2 k3s の pod から `api.github.com:443` への TCP 通信がタイムアウト:

```bash
# pod 内で実行
curl -v https://api.github.com/...
# → Connection timed out
```

一方、ICMP ping は成功:

```bash
ping api.github.com  # ✓ 応答
```

## 原因

WSL2 **mirrored networking mode** では、pod outbound パケットが iptables **MASQUERADE** に失敗:

- **mirrored mode**: pod が Windows ホストの IP を共有（<internal-host>）
- iptables MASQUERADE で送信元を変換しようとしても、WSL2 kernel の制限で TCP ACK が戻らない
- ICMP は kernel 処理で通るが、TCP は application layer なため詰まる

kubeadm・k3s 両方とも同じ制限。

## 解決策

**NAT networking mode に切り替え**:

`%USERPROFILE%\.wslconfig` を以下に変更（Windows 側）:

```ini
[wsl2]
networkingMode=NAT
autoProxy=false
autoStop=false
```

WSL2 を再起動:

```bash
wsl --shutdown
```

新しい IP で pod 起動（172.31.x.x 帯）。pod から TCP 443 が通るようになる。

### kubectl アクセスの復旧

WSL2 IP が変わるため、**portproxy** で <internal-host>:6443 → 新 IP:6443 を設定:

```powershell
# 動的に WSL2 IP を取得して portproxy 設定
$wslIp = (wsl -u root bash -c "ip addr show eth0 | grep -oP '(?<=inet )[0-9.]+'" ).Trim()
netsh interface portproxy add v4tov4 listenport=6443 listenaddress=<internal-host> connectport=6443 connectaddress=$wslIp
```

## 予防

- WSL2 k3s 本番デプロイは **NAT mode** で設計する
- pod から internet access が必要な場合は NAT 必須
- portproxy ルール は起動時に自動設定スクリプトで復旧（Windows Task Scheduler 登録）
- 本番ワークロードは WSL2 ではなく Linux native で
