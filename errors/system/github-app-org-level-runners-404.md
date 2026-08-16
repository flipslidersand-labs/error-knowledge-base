---
title: "GitHub App org-level runners API が 404 (user account の場合)"
tags: [github, arc, runners, auth]
severity: high
source: personal
date: "2026-08-13"
---

## 症状

ARC (Actions Runner Controller) に GitHub App 認証で flipslidersand の runners を register しようとしたが、以下のエラー:

```
error: couldn't get current server API group list:
  "orgs/flipslidersand/actions/runners/registration-token" 404 Not Found
```

## 原因

GitHub Actions runners API は **org-level** と **repo-level** の 2 つが存在:

- org-level: `/orgs/{org_name}/actions/runners/...` — organization アカウント専用
- repo-level: `/repos/{owner}/{repo}/actions/runners/...` — user or org 両対応

**flipslidersand は user account であり、org ではない** ため、org-level API は 404 を返す。

GitHub App を使用してもこの制限は変わらない（スコープ問題ではなく API 設計）。

## 解決策

GitHub App → **repo-level PAT (Personal Access Token)** に切り替え:

```yaml
# arc-github-secret (arc-runners namespace)
- name: GITHUB_TOKEN
  value: <PAT_with_repo_admin_access>
```

ARC が repo-level registration token を自動取得してランナー登録を完了。

## 予防

- **user account** で Actions runners を使う場合は **repo-level API** が必須
- GitHub App は org-level runners には有効だが、user account では repo-level PAT を使う
- 認証方式選択時に account type（user vs org）を確認する
- ARC トラブル時は以下で確認: `kubectl -n arc-runners logs -f <deployment>`
