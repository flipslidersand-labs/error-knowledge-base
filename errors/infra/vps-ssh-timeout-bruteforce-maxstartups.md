---
title: "VPS の SSH が timeout — sshd は正常稼働、原因はブルートフォース + fail2ban 停止"
tags: [vps, ssh, fail2ban, bruteforce, sakura]
severity: high
source: personal
date: "2026-07-05"
---

## 症状

sakura VPS の port 22 が全クライアントから connection timed out。
ping は応答あり。VNC コンソールで確認すると **sshd は正常に listen 中**、
fail2ban の ban は 0、UFW も 22/tcp ALLOW Anywhere のまま。
設定を何も変えていないのに、しばらくして接続が回復した。

## 原因（最有力）

1. **fail2ban が停止していた**（socket エラー。自動起動も disabled だった）
2. 無防備な状態で複数 IP からパスワード総当たり攻撃が継続
3. 未認証接続が滞留し sshd の **MaxStartups（10-100）が飽和** →
   新規接続がドロップされ、外部からは timeout に見えた
4. 攻撃側の接続が減った時点で自然回復（設定変更なしで復旧した理由）

MINIPC の autossh が 112 回連続リトライしていたのも接続枠の圧迫要因。

## 解決策

- VNC コンソール（さくら Web 管理画面 → コンソール）で内部から診断
- `systemctl restart fail2ban` → 即座に攻撃元 IP を ban 開始
- `systemctl enable fail2ban`（disabled だったのが根本の穴）

## 予防

- fail2ban は **enable まで確認**する（active だけでは再起動で消える）
- 「timeout ≠ サービス死亡」— ping OK / port timeout なら
  ①ファイアウォール ②接続枠飽和（MaxStartups）③プロバイダ側フィルタ を疑う
- 恒久対策は PasswordAuthentication=no（Issue #217）— 総当たり自体を無意味化
- autossh の連続リトライにバックオフを入れる（接続枠の自己圧迫を防ぐ）
