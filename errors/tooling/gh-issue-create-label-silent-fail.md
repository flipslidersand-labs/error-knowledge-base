---
title: "gh issue create でラベルが存在しない場合 Issue 自体も作成されない"
tags: [github-cli, gh, issues]
severity: medium
source: personal
date: "2026-08-02"
---

## 症状

`gh issue create --label "security,priority:critical"` を実行したとき、ラベルが存在しないリポジトリでは以下の警告だけ出て Issue が作成されなかった。

```
could not add label: 'security' not found
could not add label: 'priority:critical' not found
```

終了コードは 0 のように見えたが、実際には Issue が作成されていなかった。

## 原因

`gh issue create` は `--label` でラベルが見つからない場合、処理全体を中断する（警告を出して終了するが Issue は未作成）。

## 解決策

ラベルなしで作成するか、`gh api` を直接使う:

```bash
# ラベルなしで作成
gh issue create --title "..." --body "..."

# または gh api 経由（ラベルを省略すれば確実に作成される）
gh api repos/<owner>/<repo>/issues -X POST \
  -f title="..." \
  -f body="..."
```

ラベルが必要な場合は Issue 作成後に別途付与:

```bash
gh issue edit <number> --add-label "security" --repo <owner>/<repo>
```

## 予防

ラベルが存在しないリポジトリで `gh issue create --label` を使わない。
`gh api` 経由の POST は `--label` オプションがないため、ラベル未存在でも失敗しない。
