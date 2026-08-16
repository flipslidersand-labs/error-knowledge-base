---
title: "yukilabs-core リポジトリへの push が 403 になる"
tags: [github, git, authentication, gopass]
severity: medium
source: personal
date: "2026-06-17"
---

# 症状

```
remote: Permission to yukilabs-core/api-server.git denied to flipslidersand.
fatal: unable to access '...': The requested URL returned error: 403
```

SSH でも同様に denied（dev-teams-ordeamo アカウント）。

# 原因

- `gh` CLI は `flipslidersand` アカウントで認証 → yukilabs-core org に READ のみ
- SSH キーは `dev-teams-ordeamo` に紐づくが、こちらも yukilabs-core への push 権限なし
- keyring に flipslidersand 認証が保存されており、credential helper を上書きしてしまう

# 解決策

gopass に登録済みの yukilabs-core PAT を URL に直接埋め込む。

```bash
PAT=$(gopass show github/yukilabs-core/pat)
git push "https://x-access-token:${PAT}@github.com/yukilabs-core/api-server.git" main
```

# 予防

yukilabs-core 配下のリポジトリは毎回この方法で push する。
remote URL を SSH に変更しても解決しないので注意。
