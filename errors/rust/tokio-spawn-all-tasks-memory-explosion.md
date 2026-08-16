---
title: "tokio::spawn で全タスクを事前生成するとメモリ爆発"
tags: [rust, tokio, async, memory]
severity: high
source: personal
date: "2026-07-09"
---

## 症状

Rust の非同期クローラーで 49 URL を処理しようとしたら、11.5GB + CPU 100% で爆走し OOM 終了。
`tokio::spawn` でセマフォ付き並列実行を実装していた。

## 原因

```rust
// ❌ 悪いパターン
let sem = Arc::new(Semaphore::new(workers)); // workers=4
let mut handles = Vec::with_capacity(urls.len());
for url in urls {
    handles.push(tokio::spawn(async move {
        let _permit = sem.acquire().await.unwrap();
        fetch_page(&client, url, min_chars).await
    }));
}
// results を順序通りに処理
for handle in handles {
    let result = handle.await.unwrap();
    // ...
}
```

問題点が2つ：

1. `tokio::spawn` で49タスクを即座に全生成 → メモリに全タスク乗る
2. `for handle in handles` が **先頭から順番**に await するため、後続タスクの完了結果（HTML・DOM）が先頭タスクの完了を待ちながら全部メモリに滞留
3. HTML パース（`scraper` crate）が CPU バウンド処理を async スレッドでブロック → CPU 飽和

## 解決策

`futures::stream::buffer_unordered` で同時タスク数を制限し、完了した順に処理：

```rust
use futures::stream::{self, StreamExt};

// ✅ 正しいパターン
let mut stream = stream::iter(urls)
    .map(|url| {
        let client = Arc::clone(&client);
        async move { fetch_page(&client, url, min_chars).await }
    })
    .buffer_unordered(workers); // 同時 workers 件のみ future を保持

while let Some(result) = stream.next().await {
    // 完了順に即処理 → 結果がメモリに溜まらない
}
```

加えて：

- `tokio::task::spawn_blocking` で CPU バウンドの HTML パースをブロッキングスレッドへ移動
- `reqwest` にレスポンスサイズ上限（5MB）を追加

```toml
# Cargo.toml
futures = "0.3"
```

## 予防

- `tokio::spawn` + セマフォの組み合わせは「並列数制限」に見えるが、全タスクを spawn した時点でメモリを確保してしまう
- 並列数制限は `buffer_unordered(N)` が正解。`throttle` や `semaphore` は HTTP リクエスト数制限には使えるが、メモリ使用量制限には不十分
- CPU バウンド処理（HTML パース、圧縮、暗号化）は `spawn_blocking` を使う
