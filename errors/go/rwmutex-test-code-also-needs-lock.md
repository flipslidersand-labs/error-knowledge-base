---
title: "sync.RWMutex: テストコードもロックを取らないと -race で検出される"
tags: [go, race, sync, testing]
severity: medium
source: personal
date: "2026-08-16"
---

## 症状

本番コードの package-level 変数読み取りを `sync.Mutex` → `sync.RWMutex` に変更して
`initMu.RLock()` / `RUnlock()` に更新したが、テストコードの同じ変数への直接アクセスが
残っており `-race` で data race が報告される。

```
DATA RACE
Read at 0x... by goroutine N:
  transfer.TestXxx.func1()
      internal/transfer/session_isolation_test.go:294
Write at 0x... by goroutine M:
  transfer.InitSession()
      internal/transfer/session.go:44
```

## 原因

production code を直した後、test code での `sessionIdentity` への直接読み取りを
ロックで保護し忘れた。テストは同一パッケージにあるため package-private 変数に
直接アクセスできるが、race detector は白黒つけず全アクセスを検査する。

## 解決策

テストコード内でも package-level 変数を読む箇所に同じロックを取る。

```go
// NG
savedKey := sessionIdentity

// OK
initMu.RLock()
savedKey := sessionIdentity
initMu.RUnlock()
```

## 予防

`sync.RWMutex` へ移行するときは production code だけでなく `_test.go` ファイル内の
同変数アクセス箇所も grep して全てロックを追加する。
