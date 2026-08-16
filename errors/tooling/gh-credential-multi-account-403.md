---
title: "gh auth git-credential が ~/.git-credentials より優先され別 org への push が 403"
tags: [git, credential, gh-cli, multi-account, github]
severity: medium
source: personal
date: "2026-07-27"
---

## 症状

`git push origin <branch>` が以下で失敗する:

```
remote: Permission to yukilabs-core/knowledge-db.git denied to flipslidersand.
fatal: unable to access '...': The requested URL returned error: 403
```

`~/.git-credentials` に `https://yukilabs-core:<PAT>@github.com` が存在するのに、
`flipslidersand` として認証されてしまう。

## 原因

`gh auth login` が `~/.gitconfig` に以下を書き込む:

```
[credential "https://github.com"]
    helper =
    helper = !/usr/bin/gh auth git-credential
```

この設定が `credential.helper=store` より優先され、gh のアクティブアカウント
（この場合 `flipslidersand`）で認証される。
`-c credential.helper=...` で override しても `credential.https://github.com.helper`
が残るため効かない。

## 解決策

push URL に直接 PAT を埋め込んでクレデンシャルヘルパーをバイパス:

```bash
CRED=$(grep 'yukilabs-core' ~/.git-credentials | sed 's|https://yukilabs-core:\(.*\)@github.com|\1|')
git push "https://yukilabs-core:${CRED}@github.com/yukilabs-core/repo.git" branch-name
```

## 予防

- 複数 GitHub アカウントを扱うリポジトリでは、remote URL に username を含める:
  `git remote set-url origin https://yukilabs-core@github.com/yukilabs-core/repo.git`
- または `gh auth switch --user yukilabs-core` でアクティブアカウントを切り替えてから push
- PAT は gopass に登録しておくと取り出しやすい
