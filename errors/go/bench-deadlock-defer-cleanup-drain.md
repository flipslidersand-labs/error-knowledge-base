---
title: "Go benchmark: defer cleanup() でドレイン goroutine がデッドロック"
tags: [go, benchmark, channel, goroutine]
severity: medium
source: personal
date: "2026-08-16"
---

## 症状

`b.RunParallel` / `b.Run` 内で pipe を使った benchmark を書き、
`defer cleanup()` でパイプを閉じる + `<-done` でドレイン goroutine の終了を待つ構造にすると
benchmark が終わらずデッドロックする。

## 原因

`defer` はスコープ（関数）を抜けるまで実行されない。
`<-done` でブロックしている間は関数が終わらないため `cleanup()` も呼ばれず、
ドレイン goroutine は EOF を受け取れずに永遠にブロックする。

```go
// NG: defer は <-done より後に実行されるのでデッドロック
defer cleanup()
<-done
```

## 解決策

`cleanup()` を `<-done` の直前に明示的に呼ぶ。

```go
// OK
cleanup() // pipe を閉じて drain goroutine に EOF を届ける
<-done
```

`defer` を使う場合は `<-done` より先に実行されるよう別関数に切り出すか、
クロージャ内で明示的に呼ぶ。

## 予防

benchmark でパイプ + ドレイン goroutine の組み合わせは `defer cleanup()` ではなく
常に明示的 `cleanup(); <-done` のパターンを使う。
