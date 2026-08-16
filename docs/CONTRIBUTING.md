# 貢献ガイド（CONTRIBUTING）

このリポジトリへのエラー記録に際し、以下のガイドをお読みください。

---

## エラー記録の基本

### 目的

このリポジトリは、実装中に踏んだエラーを**ナレッジ化**し、
同じ問題を回避できるようにするためのものです。

---

## ステップバイステップ

### 1. テンプレートをコピーする

```bash
cp docs/ERROR_TEMPLATE.md errors/[category]/[error-name].md
```

**カテゴリ選択**:

- `python/` — Python, pip, venv など
- `javascript/` — Node.js, npm, JavaScript など
- `go/` — Go, modules, build など
- `rust/` — Rust, cargo, tokio など
- `database/` — SQL, MongoDB, PostgreSQL など
- `deployment/` — デプロイ, Docker, k8s, ARC など
- `ci/` — CI パイプライン, runner, Actions ワークフローなど
- `infra/` — VPS, ネットワーク, Vault, SSH, WSL2 など
- `system/` — OS, 環境変数、PATH, 権限など
- `github/` — GitHub の PR/Issue/権限まわりの挙動など
- `tooling/` — git, pnpm, husky, worktree など
- `runtime/` — ライブラリ API 変更・実行時挙動など
- `other/` — その他

### 2. フロントマターを記入する

ファイル冒頭の YAML ブロックを埋めてください。

```yaml
---
title: "エラータイトル（簡潔に）"
tags: [python, pip, venv]
severity: high       # high / medium / low
source: personal     # personal（実体験）/ web（参考）
date: "2026-08-16"
---
```

| フィールド | 説明 |
|---|---|
| `title` | エラーを一言で表すタイトル |
| `tags` | 関連技術（複数可） |
| `severity` | `high` / `medium` / `low` |
| `source` | `personal`（自分が踏んだ）/ `web`（参考情報） |
| `date` | 発生日 YYYY-MM-DD |

### 3. 本文を記入する

`## 症状` → `## 原因` → `## 解決策` → `## 予防` の順で記述します。

```markdown
## 症状

ModuleNotFoundError: No module named 'numpy'

## 原因

venv が不完全な状態で残っていた。

## 解決策

venv を削除して再作成。

    rm -rf venv/
    python -m venv venv

## 予防

- セットアップ手順に「venv 再作成コマンド」を追記する
```

### 4. 個人情報をマスキングする

公開リポジトリのため、以下は必ずマスキングしてください。

| 種別 | NG 例 | OK 例 |
|---|---|---|
| トークン | `Bearer eyJhbGci...` | `[JWT_TOKEN]` |
| 内部ホスト | `prod-db.internal:5432` | `[INTERNAL_DB_HOST]:5432` |
| ユーザー ID | `jiro@company.com` | `[USER_EMAIL]` |
| 社内パス | `/home/jiro/company/...` | `[PROJECT_PATH]` |

コミット前の確認コマンド:

```bash
grep -ri "password\|token\|@company\|internal\|prod-db" errors/
```

---

## ファイル命名規則

```
errors/[category]/[error-type]-[brief-description].md
```

- 小文字・ハイフン区切り
- アンダースコア不使用
- 例: `errors/python/venv-activate-not-found.md`

---

## コミットメッセージ

```bash
git commit -m "feat: add error record for [brief-description]"   # 新規
git commit -m "fix: update error record - [filename]"            # 更新
```

---

## 感謝

ナレッジの共有で開発効率が向上します。ありがとうございます！
