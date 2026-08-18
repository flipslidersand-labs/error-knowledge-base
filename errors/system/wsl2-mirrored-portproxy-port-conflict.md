---
title: "WSL2 mirrored networking で portproxy が Ollama の port を先取りして起動不可"
tags: [wsl2, portproxy, ollama, windows, mirrored-networking]
severity: high
source: personal
date: "2026-08-08"
---

## 症状

DS1 で Ollama が WSL2 内で "address already in use" で起動失敗。
LAN から <internal-host>:11434 に TCP は繋がるが HTTP はコネクションリセット。

## 原因

`netsh interface portproxy add v4tov4 listenport=11434 connectaddress=127.0.0.1` を設定すると、
mirrored networking モードでは Windows の svchost(iphlpsvc) が先に `0.0.0.0:11434` を確保する。
WSL2 から見た 127.0.0.1:11434 も同じ network namespace のため、Ollama が bind できない。

## 解決策

**mirrored networking で Ollama が直接 0.0.0.0:11434 をリッスンするサービスには portproxy を設定しない。**

`netsh interface portproxy delete v4tov4 listenport=11434 listenaddress=0.0.0.0`

その後 Ollama を再起動すれば LAN から直接アクセス可能になる。

## 予防

`scripts/ds1/setup-portproxy.ps1` から port 11434 を除外済み。
mirrored networking 環境では WSL2 サービスが `0.0.0.0` で bind するポートには portproxy 不要。
portproxy が必要なのは NAT モード時か、ポート変換（2222→22 など）が必要な場合のみ。
