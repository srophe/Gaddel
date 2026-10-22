#!/usr/bin/env python3
"""
Build project-news.json (the internal Project News archive) from the raw
WordPress REST export in ./blog-export/posts-page-*.json.

Output item shape (rich archive, newest first):
    { "title": <plain text>, "date": "YYYY-MM-DD", "content": <html string> }

Decisions baked in (per project requirements, 2026-10-22):
  - No "link" field. blog.syriaca.org is being decommissioned, so we do NOT
    reference it anywhere.
  - Titles are HTML-entity-decoded to plain text (e.g. &#8220; -> ").
  - Post body HTML (content.rendered) is preserved so past news survives the
    blog's deletion, BUT any <a href="...blog.syriaca.org..."> links in the
    body are unwrapped to plain text (the targets will 404 once the blog is
    gone). External links (Google Forms, TAMU, etc.) are left intact.
"""
import json, glob, re, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(HERE, "blog-export")
OUT = os.path.join(HERE, "project-news.json")

# Unwrap <a ...blog.syriaca.org...>TEXT</a>  ->  TEXT  (keep inner text/html)
BLOG_LINK = re.compile(
    r'<a\b[^>]*href=["\'][^"\']*blog\.syriaca\.org[^"\']*["\'][^>]*>(.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)

def neutralize_blog_links(body: str) -> str:
    prev = None
    # loop in case of nested/sequential matches
    while prev != body:
        prev = body
        body = BLOG_LINK.sub(r"\1", body)
    return body

def load_posts():
    posts = []
    for f in sorted(glob.glob(os.path.join(EXPORT_DIR, "posts-page-*.json"))):
        with open(f, encoding="utf-8") as fh:
            posts.extend(json.load(fh))
    return posts

def main():
    posts = load_posts()
    items = []
    for p in posts:
        if p.get("type") != "post" or p.get("status") != "publish":
            continue
        title = html.unescape((p.get("title") or {}).get("rendered", "")).strip()
        date = (p.get("date") or "")[:10]  # YYYY-MM-DD
        content = (p.get("content") or {}).get("rendered", "")
        content = neutralize_blog_links(content).strip()
        items.append({"title": title, "date": date, "content": content})

    # newest first
    items.sort(key=lambda x: x["date"], reverse=True)

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(items, fh, ensure_ascii=False, indent=2)

    print(f"Wrote {len(items)} posts to {OUT}")

if __name__ == "__main__":
    main()
