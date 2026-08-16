---
title: "MINIPC の gopass は dev 機と別ストア — SSH 先で gopass ls が空になる"
tags: [gopass, minipc, secrets, ssh]
severity: low
source: personal
date: "2026-08-03"
---

## 症状

dev 機で `gopass ls` すると infra/discord/\* 等が見えるが、
`ssh minipc "gopass ls"` は何も返らない（空出力）。

## 原因

gopass は `~/.password-store` をユーザーごとに管理する。
MINIPC の yuki ユーザーは独立した gopass ストアを持っており、
dev 機のエントリとは別管理になっている。
MINIPC 側には `infra/discord/webhook-decompose` 等の一部エントリのみ登録されている。

## 解決策

MINIPC に新しいシークレットを登録する場合は `ssh minipc "gopass insert <path>"` で直接挿入する。
または dev 機の gopass エントリを `gopass sync` / `gopass recipients` で共有する（GPG キーが必要）。

## 予防

ssh 先で gopass を使うスクリプトを書く前に、
`ssh <host> "gopass ls <path> 2>/dev/null || echo NOT_FOUND"` で存在確認を先行する。
