---
title: "actionlint: YAML config の `ignore` キーは未サポート"
tags: [tooling]
severity: medium
source: personal
---

# actionlint: YAML config の `ignore` キーは未サポート

## 症状

`.github/actionlint.yaml` に `ignore: ["SC2016"]` を追加しても
actionlint がエラーを抑制しない。

## 環境

- actionlint v1.7.12（Docker: rhysd/actionlint:latest）
- `.github/actionlint.yaml` で `ignore` キーを使用

## 原因

`ignore` は actionlint の YAML config file では**サポートされていない**キー。
CLI フラグ `-ignore <regexp>` としてのみ有効。

```yaml
# ❌ 機能しない（YAML config では無視される）
ignore:
  - "SC2016"
```

```bash
# ✅ 機能する（CLI フラグ）
actionlint -ignore "SC2016" .github/workflows/*.yml
docker run --rm -v "$(pwd):/repo" -w /repo rhysd/actionlint:latest -ignore "SC2016"
```

## 関連: ファイル先頭の shellcheck disable も機能しない

actionlint は shellcheck 実行時にシェバン行（`#!/bin/bash`）を注入する。
そのため `run: |` ブロック先頭の `# shellcheck disable=SC2016` は
「ファイル全体への適用」ではなく「次の1行のみ」の disable として機能してしまう。

```yaml
# ❌ 機能しない（ファイル全体 disable を意図しているが無効）
run: |
  # shellcheck disable=SC2016
  set -euo pipefail
  ...
```

## 解決策

問題行の**直前**に per-line disable コメントを追加する。

```bash
# shellcheck disable=SC2016
echo "$FULL_DIFF" | awk -v pat="$pat" '
  /^diff --git / { found = (substr($0, ...) == pat) }
  found { print }
'
```

## SC2016 の実際の誤検知原因

マークダウン用バッククォートが単引用符内にある場合、
shellcheck がコマンド置換（`` `cmd` ``）と誤判定して SC2016 を発生させる。

```bash
# ❌ SC2016 誤検知（バッククォートがコマンド置換に見える）
printf 'ファイル `%s` の diff をレビュー...'

# ✅ per-line disable で解消
# shellcheck disable=SC2016
printf 'ファイル `%s` の diff をレビュー...'
```

## 参照

- PR #374 (fix): SC2016 per-line disable 4箇所追加
- 2026-08-02 セッション
