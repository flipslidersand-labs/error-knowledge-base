# Error Knowledge Base

実装中に踏んだエラーをナレッジ化するリポジトリです。  
個人環境で発生したエラーを記録し、会社のネットワークからでも検索・参照できます。

---

## 概要

### 目的

- 🔁 **同じエラーを何度も踏まない** → 時間の無駄を削減
- 🔍 **エラーの原因と解決策を素早く検索** → トラブルシューティング時間を短縮
- 📚 **チーム間でナレッジを共有** → 他の開発者も参考にできる
- 🌐 **どこからでもアクセス可能** → 個人環境と会社のネットワーク両対応

### 構成

```
error-knowledge-base/
├── errors/                      # エラー記録（Markdown）
│   ├── python/                  # Python 関連
│   ├── javascript/              # JavaScript/Node.js 関連
│   ├── database/                # データベース関連
│   ├── deployment/              # デプロイメント関連
│   ├── system/                  # OS/システム関連
│   └── other/                   # その他
├── docs/                        # ドキュメント
│   ├── ERROR_TEMPLATE.md        # エラー記録テンプレート
│   └── CONTRIBUTING.md          # 貢献ガイド
├── scripts/                     # ユーティリティスクリプト
│   └── build.py                 # Markdown → HTML 変換
├── .github/workflows/           # GitHub Actions
│   └── deploy.yml               # GitHub Pages 自動デプロイ
└── README.md                    # このファイル
```

---

## クイックスタート

### 1. リポジトリをセットアップ

```bash
bash setup-repo.sh [your-github-username]
cd error-knowledge-base
```

### 2. 最初の commit をプッシュ

```bash
git add .
git commit -m "Initial commit: error knowledge base setup"
git branch -M main
git push -u origin main
```

### 3. GitHub Pages を有効化

GitHub のリポジトリ設定で：
- **Settings** → **Pages**
- **Build and deployment** → **Branch** を `main` に設定
- **Root** を選択

これで自動的に `https://[username].github.io/error-knowledge-base` に公開されます。

---

## 使い方

### エラーを記録する

1. **テンプレートをコピー**

   ```bash
   cp docs/ERROR_TEMPLATE.md errors/python/my-error.md
   ```

2. **情報を記入**

   - エラーメッセージ / 症状
   - 環境情報（Python バージョンなど）
   - 原因分析
   - 解決策（試した方法、最終的な解決法）
   - 予防策
   - 参考リンク

3. **個人情報をマスキング**

   ```markdown
   ❌ DatabaseError: Could not connect to postgresql://user:password@db.company.com/mydb
   ✅ DatabaseError: Could not connect to postgresql://[USER]:[PASS]@[HOST]/[DB]
   ```

4. **commit & push**

   ```bash
   git add errors/python/my-error.md
   git commit -m "docs: add error record for Python import issue"
   git push
   ```

   → GitHub Pages に自動で反映されます（数秒後）

### エラーを検索する

**Web UI から検索**（GitHub Pages）
- `https://[username].github.io/error-knowledge-base`
- カテゴリで絞り込み
- ブラウザの検索機能（Ctrl+F / Cmd+F）で内容検索

**GitHub 上で検索**
- リポジトリの検索バーを使用
- ファイル内容全体が検索対象

---

## ファイル名の規則

エラー記録ファイルは、以下の規則で命名してください：

```
errors/[category]/[error-type]-[brief-description].md

例:
- errors/python/import-error-module-not-found.md
- errors/database/connection-timeout-postgresql.md
- errors/deployment/github-pages-build-failed.md
- errors/javascript/node-gyp-compilation-error.md
```

**規則**
- 小文字のみ
- スペースはハイフンで表現
- エラーの種類と簡潔な説明を含める

---

## テンプレート項目の説明

| 項目 | 説明 |
|------|------|
| **基本情報** | プロジェクト名、環境、OS、発生時期 |
| **症状** | 実際のエラーメッセージやスタックトレース |
| **原因** | 根本原因は何だったか。チェックボックスで分類 |
| **解決策** | 試した方法（失敗含む）と最終的な解決法 |
| **予防** | 次から踏まないための対策。自動化できることがあるか |
| **参考リンク** | 公式ドキュメント、StackOverflow、関連 Issue など |

---

## 個人情報の取り扱い

リポジトリは **GitHub で公開** されます。  
**絶対に以下を記載してはいけません**：

- ❌ パスワード、API キー、トークン
- ❌ 内部サーバーの実際のホスト名・IP アドレス
- ❌ ユーザー ID や実名（記録者名は OK）
- ❌ 会社の社内システム固有情報
- ❌ ビジネス上の機密情報

**マスキング例**：

```markdown
❌ Failed to connect to prod-db-01.internal.company.com
✅ Failed to connect to [INTERNAL_DB_HOST]

❌ Authentication failed: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
✅ Authentication failed: Invalid JWT token

❌ Error in company/finance/salary-calc module
✅ Error in [INTERNAL_MODULE]
```

---

## 実装フェーズ

### Phase 1: 基盤構築 ✅

- GitHub リポジトリ構造
- エラー記録テンプレート
- GitHub Actions ワークフロー（自動デプロイ）
- README ドキュメント

### Phase 2: Web 化（自動）

GitHub Pages で Markdown が自動的に HTML に変換・公開されます。

### Phase 3: 検索・分類（将来）

- タグシステムの追加
- フルテキスト検索
- カテゴリ別ナビゲーション
- 関連エラー表示

### Phase 4: 運用（継続）

- エラー記録の定期レビュー
- 重複排除
- ドキュメンテーション改善
- チームフィードバック

---

## よくある質問

### Q: 古いエラー記録は削除すべき？

**A**: 削除不要です。解決済みのエラーも参考価値があります。  
ただし、**大量に似たエラー** がある場合は、統合・重複排除を検討してください。

### Q: 記録は毎回 Web で確認する必要がある？

**A**: いいえ。GitHub 上で直接 Markdown ファイルを読むこともできます。  
Web UI は見やすさと複数エラーの横断検索が利点です。

### Q: 会社のネットワークから見えないことはない？

**A**: GitHub は公開リポジトリなので、どのネットワークからでもアクセス可能です。  
（ただし、会社がアウトバウンドを制限している場合は別）

### Q: プライベートリポジトリにしたい場合は？

**A**: GitHub Settings で Private に変更できます。  
ただしそれでは「会社から気軽にアクセス」という目的が達成できません。  
機密情報は絶対に記載しないアプローチで公開版がおすすめです。

---

## 貢献ガイド

エラーを記録するときの注意事項：

1. **テンプレートを使う** → 記録の統一性
2. **個人情報をマスキング** → 公開前に確認
3. **分かりやすく書く** → 他の開発者が理解できるように
4. **参考リンク付け** → 出典・根拠を示す

---

## トラブルシューティング

### GitHub Pages が反映されない

1. **Actions を確認**  
   GitHub → **Actions** → 最新の `Deploy to GitHub Pages` が ✅ 成功しているか

2. **ブランチ設定を確認**  
   GitHub → **Settings** → **Pages** → `main` ブランチが選択されているか

3. **キャッシュをクリア**  
   ```bash
   Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)
   ```

### build.py でエラーが出る

```bash
# 必要なパッケージをインストール
pip install -r requirements.txt
python scripts/build.py
```

---

## ライセンス

このリポジトリはドキュメント集なので特定のライセンスは不要ですが、  
参考資料として他のプロジェクトから引用する場合はそのライセンスを尊重してください。

---

## 関連リソース

- [GitHub Pages 公式ドキュメント](https://pages.github.com/)
- [Markdown チートシート](https://www.markdownguide.org/basic-syntax/)
- [Python Markdown](https://python-markdown.github.io/)

---

**最終更新**: 2024  
**マネージャー**: [Your Name]
