"""Blog serving module — renders markdown blog posts as HTML pages."""

import os
import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

blog_router = APIRouter()

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content")
BLOG_BASE = "/blog"


def _parse_markdown(content: str) -> str:
    """Simple markdown to HTML converter."""
    # Remove meta title/description for display
    content = re.sub(r'^## Meta Title\n.*\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^## Meta Description\n.*\n', '', content, flags=re.MULTILINE)

    lines = content.split('\n')
    html = []
    in_code = False
    in_table = False
    in_list = False
    list_tag = ''

    for line in lines:
        # Code blocks
        if line.startswith('```'):
            if in_code:
                html.append('</code></pre>')
                in_code = False
            else:
                html.append('<pre><code>')
                in_code = True
            continue

        if in_code:
            html.append(line)
            continue

        # Tables
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                html.append('<table>')
                in_table = True
            is_header = bool(re.match(r'^\|[\s\-:]+\|', line))
            if is_header:
                continue
            cells = [c.strip() for c in line.split('|')[1:-1]]
            tag = 'th' if '---' in line else 'td'
            html.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>')
            continue
        elif in_table:
            html.append('</table>')
            in_table = False

        # Close list if not a list item
        if in_list and not line.strip().startswith(('- ', '* ', '1. ')):
            html.append(f'</{list_tag}>')
            in_list = False

        # Headers
        if line.startswith('# '):
            html.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            html.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            html.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#### '):
            html.append(f'<h4>{line[5:]}</h4>')
        # Unordered list
        elif line.strip().startswith('- '):
            if not in_list:
                html.append('<ul>')
                in_list = True
                list_tag = 'ul'
            html.append(f'<li>{_inline_format(line.strip()[2:])}</li>')
        # Ordered list items
        elif re.match(r'^\d+\. ', line.strip()):
            if not in_list:
                html.append('<ol>')
                in_list = True
                list_tag = 'ol'
            text = re.sub(r'^\d+\. ', '', line.strip())
            html.append(f'<li>{_inline_format(text)}</li>')
        # Checkbox
        elif line.strip().startswith('- [ ]') or line.strip().startswith('- [x]'):
            checked = 'checked' if '[x]' in line else ''
            text = line.strip()[6:]
            html.append(f'<div class="check-item"><input type="checkbox" {checked} disabled> {text}</div>')
        # Horizontal rule
        elif line.strip() == '---':
            html.append('<hr>')
        # Empty line
        elif not line.strip():
            html.append('')
        # Strong/emphasis
        elif line.strip().startswith('**') and line.strip().endswith('**'):
            html.append(f'<p><strong>{line.strip()[2:-2]}</strong></p>')
        # Regular paragraph
        else:
            html.append(f'<p>{_inline_format(line)}</p>')

    if in_list:
        html.append(f'</{list_tag}>')
    if in_table:
        html.append('</table>')

    return '\n'.join(html)


def _inline_format(text: str) -> str:
    """Format inline markdown elements."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Links
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    return text


def _get_blog_files() -> list[dict]:
    """Get all blog post files with metadata."""
    posts = []
    if not os.path.isdir(BLOG_DIR):
        return posts

    for fname in sorted(os.listdir(BLOG_DIR), reverse=True):
        if not fname.startswith('blog-') or not fname.endswith('.md'):
            continue
        fpath = os.path.join(BLOG_DIR, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title from first heading
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else fname.replace('.md', '')

        # Extract meta description
        desc_match = re.search(r'^## Meta Description\n(.+)$', content, re.MULTILINE)
        description = desc_match.group(1) if desc_match else ''

        slug = fname.replace('.md', '')

        # Clean up title for display
        clean_title = re.sub(r'^SEO Blog \d+: ', '', title)
        clean_title = clean_title.strip('"')

        posts.append({
            "slug": slug,
            "title": clean_title,
            "full_title": title,
            "description": description,
            "file": fname,
        })

    return posts


@blog_router.get("/blog", response_class=HTMLResponse)
async def blog_index():
    """Blog listing page."""
    posts = _get_blog_files()

    post_html = ''
    for p in posts:
        post_html += f'''
        <article class="blog-card">
            <h2><a href="/blog/{p['slug']}">{p['title']}</a></h2>
            <p class="blog-desc">{p.get('description', '')}</p>
            <a href="/blog/{p['slug']}" class="blog-link">Read more →</a>
        </article>'''

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Listify Blog — 跨境电商 Listing 优化指南</title>
    <meta name="description" content="跨境电商 Listing 优化、SEO 关键词、多平台运营指南。覆盖 Amazon、Shopify、Temu、TikTok Shop 的完整教程和模板。">
    <meta property="og:title" content="Listify Blog — 跨境电商 Listing 优化指南">
    <meta property="og:description" content="跨境电商 Listing 优化、SEO 关键词、多平台运营指南。免费 AI Listing 生成工具。">
    <meta property="og:type" content="website">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://listify.ai/blog">
    <link rel="stylesheet" href="/static/style.css">
    <style>
        .blog-header {{ text-align: center; padding: 40px 20px 20px; }}
        .blog-header h1 {{ font-size: 2em; color: var(--primary); }}
        .blog-grid {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .blog-card {{
            background: var(--card); border-radius: 12px; padding: 24px;
            margin-bottom: 16px; box-shadow: var(--shadow);
        }}
        .blog-card h2 {{ margin-bottom: 8px; font-size: 1.2em; }}
        .blog-card h2 a {{ color: var(--text); text-decoration: none; }}
        .blog-card h2 a:hover {{ color: var(--primary); }}
        .blog-desc {{ color: var(--text-light); font-size: 14px; margin-bottom: 12px; }}
        .blog-link {{ color: var(--primary); font-weight: 600; text-decoration: none; font-size: 14px; }}
        .blog-post {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
        .blog-post h1 {{ font-size: 2em; margin-bottom: 20px; }}
        .blog-post h2 {{ font-size: 1.4em; margin-top: 32px; margin-bottom: 12px; color: var(--primary); }}
        .blog-post h3 {{ font-size: 1.1em; margin-top: 24px; }}
        .blog-post p {{ margin-bottom: 16px; line-height: 1.8; }}
        .blog-post ul, .blog-post ol {{ margin: 12px 0 20px 24px; }}
        .blog-post li {{ margin-bottom: 8px; line-height: 1.7; }}
        .blog-post table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }}
        .blog-post th {{ background: var(--primary); color: white; padding: 10px 12px; text-align: left; }}
        .blog-post td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); }}
        .blog-post tr:nth-child(even) td {{ background: var(--bg); }}
        .blog-post code {{ background: var(--bg); padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
        .blog-post pre {{ background: #2D3436; color: #DFE6E9; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 16px 0; }}
        .blog-post hr {{ border: none; border-top: 1px solid var(--border); margin: 32px 0; }}
        .blog-post strong {{ color: var(--text); }}
        .check-item {{ margin: 4px 0; color: var(--text-light); }}
        .blog-post blockquote {{
            border-left: 3px solid var(--primary); padding: 8px 16px;
            margin: 16px 0; background: var(--bg); border-radius: 0 8px 8px 0;
            color: var(--text-light);
        }}
        .back-link {{ display: inline-block; margin-bottom: 20px; color: var(--primary); text-decoration: none; }}
        .cta-banner {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 32px; border-radius: 12px; text-align: center; margin: 32px 0;
        }}
        .cta-banner a {{ color: #FFD700; font-weight: 700; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo"><a href="/" style="text-decoration:none;color:inherit;">📦 Listify</a></div>
        <div class="tagline">跨境电商 Listing 优化博客</div>
        <div class="nav-right"><a href="/" style="color:var(--primary);text-decoration:none;">← 回到工具</a></div>
    </nav>

    <div class="blog-header">
        <h1>📝 Listify Blog</h1>
        <p style="color:var(--text-light);">跨境电商 Listing 优化 · SEO · 多平台运营指南</p>
    </div>

    <div class="blog-grid">
        {post_html}
    </div>

    <footer><p>Powered by Listify AI · <a href="/">返回工具</a></p></footer>
</body>
</html>'''


@blog_router.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(slug: str):
    """Individual blog post page."""
    fpath = os.path.join(BLOG_DIR, f"{slug}.md")
    if not os.path.isfile(fpath):
        raise HTTPException(404, "Blog post not found")

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title from first heading
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else slug
    # Remove SEO Blog prefix for display
    display_title = re.sub(r'^SEO Blog \d+: ', '', title)
    display_title = display_title.strip('"')

    # Extract meta description for SEO
    meta_desc_match = re.search(r'^## Meta Description\n(.+)$', content, re.MULTILINE)
    meta_description = meta_desc_match.group(1) if meta_desc_match else display_title

    # Remove the first heading line and meta lines before parsing
    body_content = content
    if title_match:
        body_content = content[:title_match.start()] + content[title_match.end():]
    body_html = _parse_markdown(body_content)

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_title} — Listify Blog</title>
    <meta name="description" content="{meta_description}">
    <meta property="og:title" content="{display_title}">
    <meta property="og:description" content="{meta_description}">
    <meta property="og:type" content="article">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://listify.ai/blog/{slug}">
    <link rel="stylesheet" href="/static/style.css">
    <style>
        .blog-header {{ text-align: center; padding: 40px 20px 20px; }}
        .blog-post {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .blog-post h1 {{ font-size: 2em; margin-bottom: 20px; line-height: 1.3; }}
        .blog-post h2 {{ font-size: 1.4em; margin-top: 32px; margin-bottom: 12px; color: var(--primary); }}
        .blog-post h3 {{ font-size: 1.1em; margin-top: 24px; }}
        .blog-post p {{ margin-bottom: 16px; line-height: 1.8; }}
        .blog-post ul, .blog-post ol {{ margin: 12px 0 20px 24px; }}
        .blog-post li {{ margin-bottom: 8px; line-height: 1.7; }}
        .blog-post table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }}
        .blog-post th {{ background: var(--primary); color: white; padding: 10px 12px; text-align: left; }}
        .blog-post td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); }}
        .blog-post tr:nth-child(even) td {{ background: var(--bg); }}
        .blog-post code {{ background: var(--bg); padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
        .blog-post pre {{ background: #2D3436; color: #DFE6E9; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 16px 0; }}
        .blog-post hr {{ border: none; border-top: 1px solid var(--border); margin: 32px 0; }}
        .blog-post strong {{ color: var(--text); }}
        .check-item {{ margin: 4px 0; color: var(--text-light); }}
        .blog-post blockquote {{
            border-left: 3px solid var(--primary); padding: 8px 16px;
            margin: 16px 0; background: var(--bg); border-radius: 0 8px 8px 0;
            color: var(--text-light);
        }}
        .back-link {{ display: inline-block; margin-bottom: 20px; color: var(--primary); text-decoration: none; font-weight: 600; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo"><a href="/" style="text-decoration:none;color:inherit;">📦 Listify</a></div>
        <div class="tagline">跨境电商 Listing 优化博客</div>
        <div class="nav-right"><a href="/" style="color:var(--primary);text-decoration:none;">← 回到工具</a></div>
    </nav>

    <div class="blog-post">
        <a href="/blog" class="back-link">← 所有文章</a>
        <h1>{display_title}</h1>
        {body_html}
        <div class="cta-banner" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 32px; border-radius: 12px; text-align: center; margin: 32px 0;">
            <h2 style="color:white;">🚀 一键生成你的全平台 Listing</h2>
            <p>注册 Listify 免费试用 3 次 — Amazon · Shopify · Temu · TikTok Shop</p>
            <a href="/" style="color: #FFD700; font-weight: 700; font-size: 18px;">免费开始 →</a>
        </div>
    </div>

    <footer><p>Powered by Listify AI · <a href="/blog">Blog</a> · <a href="/">工具</a></p></footer>
</body>
</html>'''