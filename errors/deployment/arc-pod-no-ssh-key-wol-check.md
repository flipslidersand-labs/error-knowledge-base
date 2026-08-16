---
title: "ARC runner pod 内に SSH 鍵がなく WoL ping チェックが失敗"
tags: [arc, github-actions, wol, ssh, nc]
severity: medium
source: personal
date: "2026-08-05"
---

## 症状

`_wol-ds1.yml` の「DS1 オンライン確認」ステップで SSH チェックを使っていたが、
ARC runner pod 内に SSH 鍵が存在しないため常に失敗し WoL が誤ってトリガーされる。

```bash
# 失敗するコード
ssh -o ConnectTimeout=5 -o BatchMode=yes ds1 exit 2>/dev/null
```

## 原因

ARC runner は Kubernetes pod として起動する。pod 内には `~/.ssh/` が存在しない。
`BatchMode=yes` のため認証失敗で即 exit=1 → 常に「DS1 オフライン」と判定。

## 解決策

SSH の代わりに `nc` (netcat) で TCP 到達チェックを使う:

```bash
if nc -z -w3 192.168.68.60 22 2>/dev/null; then
  echo "DS1 is already online"
fi
```

- `-z`: ポートスキャンモード（データ送信なし）
- `-w3`: 3秒タイムアウト

## 予防

ARC runner job で SSH を使う処理が必要な場合はシークレットから鍵を mount するか、
TCP 到達チェックで代替できないか検討する。
