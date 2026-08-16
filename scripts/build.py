#!/usr/bin/env python3
"""
Markdown エラー記録を HTML に変換して GitHub Pages 用に出力
タグシステム・検索機能付き
"""
import os
import re
import html
import markdown
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

def parse_frontmatter(text: str) -> Tuple[Dict, str]:
    """frontmatter を YAML 形式で抽出（--- で囲まれた部分）"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not match:
        return {}, text

    frontmatter_text = match.group(1)
    body = text[match.end():]
    meta = {}

    for line in frontmatter_text.split('\n'):
        if not line.strip():
            continue
        if ':' not in line:
            continue

        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()

        # tags を list に変換 [a, b, c] 形式
        if key == 'tags':
            value = value.strip('[]').split(',')
            value = [v.strip() for v in value]

        meta[key] = value

    return meta, body

def extract_h1(body: str) -> str:
    """本文から H1 タイトルを抽出"""
    match = re.search(r'^#\s+(.+?)(?:\n|$)', body, re.MULTILINE)
    return match.group(1) if match else ""

def load_all_errors(errors_dir: Path) -> List[Dict]:
    """全エラーをロードしてメタデータを収集"""
    errors = []

    for category_dir in sorted(errors_dir.iterdir()):
        if not category_dir.is_dir():
            continue

        category_name = category_dir.name

        for md_file in sorted(category_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(text)

            # frontmatter がない場合、空の meta で処理継続
            title = meta.get('title') or extract_h1(body) or md_file.stem
            tags = meta.get('tags', [])
            severity = meta.get('severity', 'medium')
            source = meta.get('source', 'web')  # デフォルト: web

            # 検索用テキスト（本文から Markdown 記号を除去）
            search_text = sanitize_text_for_search(body)[:500]

            errors.append({
                'category': category_name,
                'stem': md_file.stem,
                'html_path': f"{category_name}/{md_file.stem}.html",
                'title': title,
                'tags': tags if isinstance(tags, list) else [],
                'severity': severity,
                'source': source,
                'meta': meta,
                'body_md': body,
                'search_text': search_text,
            })

    return errors

def sanitize_text_for_search(markdown_text: str) -> str:
    """Markdown テキストから記号を除去し、プレーンテキストに"""
    text = re.sub(r'```.*?```', ' ', markdown_text, flags=re.DOTALL)  # コードブロック
    text = re.sub(r'`[^`]+`', ' ', text)                              # インラインコード
    text = re.sub(r'#+\s+', '', text)                                 # 見出し
    text = re.sub(r'\|[^\n]+', ' ', text)                             # テーブル行
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)              # リンク
    text = re.sub(r'[-*]\s+', '', text)                               # リスト
    text = ' '.join(text.split())                                      # 正規化
    return text

def build_related(errors: List[Dict], current: Dict) -> List[Dict]:
    """関連エラーを取得（タグ共通度でソート、上位3件）"""
    def tag_score(e):
        if not e['tags'] or not current['tags']:
            return 0
        return len(set(e['tags']) & set(current['tags']))

    related = sorted(
        [e for e in errors if e['stem'] != current['stem']],
        key=tag_score,
        reverse=True
    )
    return [e for e in related if tag_score(e) > 0][:3]

def build():
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    errors_dir = Path("errors")
    errors = load_all_errors(errors_dir)

    # 全タグを集約（重複排除）
    all_tags = sorted(set(tag for e in errors for tag in e.get('tags', [])))

    # インデックス HTML を作成
    index_css = """        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
               background: #f5f5f5; color: #333; line-height: 1.6; }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        h1 { margin: 20px 0; color: #222; }
        #search-box { width: 100%; padding: 10px 14px; font-size: 1em; border: 2px solid #ddd;
                     border-radius: 8px; margin: 16px 0; box-sizing: border-box; }
        #search-box:focus { border-color: #0066cc; outline: none; }
        #tag-filter { margin: 16px 0; }
        #filter-label { font-size: 0.85em; color: #666; margin-bottom: 6px; display: block; }
        .tag { display: inline-block; background: #e8f0ff; color: #0044aa; border-radius: 12px;
               padding: 2px 10px; font-size: 0.8em; margin: 2px; cursor: pointer;
               border: 1px solid #c0d0f0; }
        .tag:hover { background: #0066cc; color: white; }
        .tag.active { background: #0066cc; color: white; }
        .severity { display: inline-block; border-radius: 4px; padding: 1px 8px; font-size: 0.75em;
                   font-weight: bold; color: white; margin-left: 6px; }
        .severity-high { background: #cc3300; }
        .severity-medium { background: #cc7700; }
        .severity-low { background: #007700; }
        .category { background: white; border-radius: 8px; padding: 20px; margin: 20px 0;
                   box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .category h2 { color: #0066cc; margin-bottom: 15px; font-size: 1.3em; }
        .category h3 { color: #0066cc; margin-bottom: 15px; font-size: 1.1em; }
        .error-card { padding: 12px 0; border-bottom: 1px solid #eee; }
        .error-card:last-child { border-bottom: none; }
        .error-card[data-hidden="true"] { display: none; }
        .error-card a { color: #0066cc; text-decoration: none; }
        .error-card a:hover { text-decoration: underline; }
        .source-badge { display: inline-block; border-radius: 4px; padding: 1px 8px; font-size: 0.7em;
                       font-weight: bold; color: white; margin-left: 4px; }
        .source-personal { background: #0066cc; }
        .source-web { background: #666666; }
        footer { text-align: center; margin-top: 40px; color: #666; font-size: 0.9em; }
    """

    index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error Knowledge Base</title>
    <style>
{index_css}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Error Knowledge Base</h1>
        <p>実装中に踏んだエラーをナレッジ化したリポジトリです。</p>

        <input id="search-box" type="text" placeholder="エラーを検索...">

        <div id="tag-filter">
            <span id="filter-label">タグで絞り込み：</span>
"""

    # タグフィルタボタンを生成
    for tag in all_tags:
        index_html += f'            <span class="tag" onclick="filterByTag(this, {repr(tag)})">{html.escape(tag)}</span>\n'

    index_html += '            <span class="tag" onclick="filterByTag(this, \'ALL\')" style="background:#eee">すべて</span>\n'
    index_html += '        </div>\n'
    index_html += '        <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">\n'

    # source ごとにグループ分け（personal -> web）
    for source_type in ['personal', 'web']:
        source_errors = [e for e in errors if e.get('source', 'web') == source_type]
        if not source_errors:
            continue

        source_label = '🎯 実体験' if source_type == 'personal' else '📚 参考・学習'
        index_html += f'        <h2 style="margin: 30px 0 15px; color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 10px;">{source_label}</h2>\n'

        # カテゴリごとにエラーカードを生成
        categories_in_source = sorted(set(e['category'] for e in source_errors))

        for category_name in categories_in_source:
            category_errors = [e for e in source_errors if e['category'] == category_name]

            if not category_errors:
                continue

            index_html += f'        <div class="category">\n'
            index_html += f'            <h3>📁 {category_name.upper()}</h3>\n'

            for error in category_errors:
                tags_str = ','.join(error.get('tags', []))
                title = html.escape(error['title'])
                search_text = html.escape(error['search_text'])
                severity = html.escape(error.get('severity', 'medium'))
                source = html.escape(error.get('source', 'web'))
                source_label = '実体験' if source == 'personal' else '参考'
                html_name = error['stem'] + ".html"

                index_html += f'            <div class="error-card" data-tags="{tags_str}" data-title="{title}" data-text="{search_text}">\n'
                index_html += f'                <a href="{error["html_path"]}">{title}</a>\n'
                index_html += f'                <span class="severity severity-{severity}">{severity}</span>\n'
                index_html += f'                <span class="source-badge source-{source}">{source_label}</span>\n'

                if error.get('tags'):
                    for tag in error['tags']:
                        index_html += f'                <span class="tag" style="cursor:pointer" onclick="filterByTag(this, {repr(tag)})">{html.escape(tag)}</span>\n'

                index_html += '            </div>\n'

            index_html += '        </div>\n'

    index_html += f"""        <footer>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><a href="https://github.com/flipslidersand-labs/error-knowledge-base">GitHub Repository</a></p>
        </footer>
    </div>

    <script>
        let activeTag = null;
        let searchQuery = '';

        function filterByTag(el, tag) {{
            if (tag === 'ALL' || activeTag === tag) {{
                activeTag = null;
                document.querySelectorAll('#tag-filter .tag').forEach(t => t.classList.remove('active'));
            }} else {{
                activeTag = tag;
                document.querySelectorAll('#tag-filter .tag').forEach(t => t.classList.remove('active'));
                el.classList.add('active');
            }}
            applyFilters();
        }}

        function applyFilters() {{
            const cards = document.querySelectorAll('.error-card');
            const q = searchQuery.toLowerCase().trim();

            cards.forEach(card => {{
                const cardTags = (card.dataset.tags || '').split(',').filter(t => t);
                const cardTitle = (card.dataset.title || '').toLowerCase();
                const cardText = (card.dataset.text || '').toLowerCase();

                const tagMatch = !activeTag || cardTags.includes(activeTag);
                const textMatch = !q || cardTitle.includes(q) || cardText.includes(q) ||
                                  cardTags.some(t => t.includes(q));

                card.dataset.hidden = !(tagMatch && textMatch);
            }});

            // カテゴリブロックを全カード非表示なら隠す
            document.querySelectorAll('.category').forEach(cat => {{
                const visible = cat.querySelectorAll('.error-card:not([data-hidden="true"])');
                cat.style.display = visible.length ? '' : 'none';
            }});
        }}

        document.getElementById('search-box').addEventListener('input', e => {{
            searchQuery = e.target.value;
            applyFilters();
        }});
    </script>
</body>
</html>
"""

    (build_dir / "index.html").write_text(index_html)

    # 各 Markdown ファイルを HTML に変換
    for error in errors:
        category_name = error['category']
        output_dir = build_dir / category_name
        output_dir.mkdir(exist_ok=True)

        html_content = markdown.markdown(
            error['body_md'],
            extensions=['tables', 'fenced_code', 'codehilite']
        )

        # 関連エラーを取得
        related = build_related(errors, error)
        related_html = ""
        if related:
            related_html = '        <div class="related-section">\n'
            related_html += '            <h2>関連するエラー</h2>\n'
            related_html += '            <ul class="related-list">\n'
            for rel in related:
                related_html += f'                <li><a href="../{rel["html_path"]}">{html.escape(rel["title"])}</a></li>\n'
            related_html += '            </ul>\n'
            related_html += '        </div>\n'

        # タグを HTML に
        tags_html = ""
        if error.get('tags'):
            for tag in error['tags']:
                tags_html += f'<span class="tag">{html.escape(tag)}</span> '

        severity = html.escape(error.get('severity', 'medium'))
        source = html.escape(error.get('source', 'web'))
        source_label = '実体験' if source == 'personal' else '参考'

        detail_css = """        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
               background: #f5f5f5; color: #333; line-height: 1.6; }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; background: white;
                    border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { color: #222; margin: 20px 0 10px; }
        h2 { color: #0066cc; margin: 20px 0 10px; font-size: 1.2em; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px;
               font-family: 'Monaco', 'Courier New', monospace; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; margin: 10px 0; }
        pre code { background: none; padding: 0; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .back { margin-bottom: 20px; }
        .back a { color: #0066cc; }
        .page-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
        .severity { display: inline-block; border-radius: 4px; padding: 1px 8px; font-size: 0.75em;
                   font-weight: bold; color: white; }
        .severity-high { background: #cc3300; }
        .severity-medium { background: #cc7700; }
        .severity-low { background: #007700; }
        .tag { display: inline-block; background: #e8f0ff; color: #0044aa; border-radius: 12px;
               padding: 2px 10px; font-size: 0.8em; margin: 2px; border: 1px solid #c0d0f0; }
        .source-badge { display: inline-block; border-radius: 4px; padding: 1px 8px; font-size: 0.7em;
                       font-weight: bold; color: white; margin-left: 6px; }
        .source-personal { background: #0066cc; }
        .source-web { background: #666666; }
        .related-section { margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee; }
        .related-section h2 { color: #555; font-size: 1.1em; margin-bottom: 12px; }
        .related-list { list-style: none; }
        .related-list li { padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
        .related-list li:last-child { border-bottom: none; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #f4f4f4; font-weight: bold; }
    """

        full_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(error['title'])}</title>
    <style>
{detail_css}
    </style>
</head>
<body>
    <div class="container">
        <div class="back"><a href="../">← インデックスに戻る</a></div>
        <div class="page-meta">
            <span>カテゴリ: <strong>{html.escape(category_name)}</strong></span>
            <span class="severity severity-{severity}">{severity}</span>
            <span class="source-badge source-{source}">{source_label}</span>
            {tags_html}
        </div>
        {html_content}
        {related_html}
    </div>
</body>
</html>
"""
        (output_dir / (error['stem'] + ".html")).write_text(full_html, encoding="utf-8")

    print(f"✅ Build complete: {build_dir}/index.html ({len(errors)} errors)")

if __name__ == "__main__":
    build()
