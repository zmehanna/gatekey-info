#!/usr/bin/env python3
"""Regenerate identical PrivateGateKey header/footer across the four public pages.

Edit site-shell/header.html and site-shell/footer.html, then run this script.
GitHub Pages serves the generated static HTML: navigation works without JS.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HEADER = (ROOT / "site-shell" / "header.html").read_text(encoding="utf-8").strip()
FOOTER = (ROOT / "site-shell" / "footer.html").read_text(encoding="utf-8").strip()
CSS = '<link rel="stylesheet" href="/assets/css/site-shell.css?v=20261116-1">'
JS = '<script defer src="/assets/js/site-shell.js?v=20261116-1"></script>'

PAGES = {
    "index.html": (
        r'<header class="top">[\s\S]*?</header>',
        r'<footer class="footer">[\s\S]*?</footer>',
    ),
    "support.html": (
        r'<header class="topbar">[\s\S]*?</header>',
        r'<footer class="footer">[\s\S]*?</footer>',
    ),
    "privacy.html": (
        r'<header class="topbar">[\s\S]*?</header>',
        r'<footer class="footer">[\s\S]*?</footer>',
    ),
    "products/privategatekey/index.html": (
        r'<nav class="pgk-nav">[\s\S]*?</nav>',
        r'<footer class="pgk-footer">[\s\S]*?</footer>',
    ),
}

def swap(text: str, old_pattern: str, component: str, kind: str) -> str:
    tag = f"PGK-SHARED-{kind.upper()}"
    wrapped = rf'<!-- {tag}:START -->[\s\S]*?<!-- {tag}:END -->'
    pattern = wrapped if f"<!-- {tag}:START -->" in text else old_pattern
    updated, found = re.subn(pattern, lambda _: component, text, count=1)
    if found != 1:
        raise RuntimeError(f"Expected one {kind}, got {found}")
    return updated

def modify(filename: str, patterns: tuple[str, str]) -> None:
    target = ROOT / filename
    html = target.read_text(encoding="utf-8")
    if filename == "index.html" and "pgk-home-locale" not in html:
        language = re.search(r'<div class="lang" aria-label="Language">[\s\S]*?</div>', html)
        if not language:
            raise RuntimeError("Cannot preserve the French/English switcher")
        # Retain the home page's language selector, but place it inside the
        # hero so the navigation stays IDENTICAL on every page.
        hero = re.search(r'<div class="hero-copy"><img[^>]+class="hero-logo"[^>]*>', html)
        if not hero:
            raise RuntimeError("Cannot locate home hero logo")
        html = html[:hero.end()] + (
            '<div class="pgk-home-locale">' + language.group(0) + '</div>'
        ) + html[hero.end():]
        html = html.replace(
            "</style>",
            ".pgk-home-locale{display:flex;justify-content:flex-start;margin:20px 0 15px}"
            ".pgk-home-locale .lang{background:#16263a;border-color:#d7b98a66}"
            "</style>",
            1,
        )
        menu_start = html.find("const m=document.getElementById('menu')")
        if menu_start < 0:
            raise RuntimeError("Legacy home nav handler is missing")
        menu_end = html.find("})();", menu_start)
        if menu_end < 0:
            raise RuntimeError("Legacy home menu handler end is missing")
        html = html[:menu_start] + html[menu_end:]
    html = swap(html, patterns[0], HEADER, "header")
    html = swap(html, patterns[1], FOOTER, "footer")
    # Old product-only shell is no longer loaded; all four pages use one
    # shared stylesheet and one shared small navigation controller.
    html = re.sub(
        r'<link[^>]+href="/assets/css/brand-site.css[^"]*"[^>]*>\s*', "", html
    )
    html = re.sub(
        r'<script[^>]+src="/assets/js/brand-site.js[^"]*"[^>]*></script>\s*', "", html
    )
    if "/assets/css/site-shell.css" not in html:
        html = html.replace("</head>", f"{CSS}\n</head>", 1)
    if "/assets/js/site-shell.js" not in html:
        html = html.replace("</head>", f"{JS}\n</head>", 1)
    target.write_text(html, encoding="utf-8")
    print(f"Updated {filename}: {len(html)} bytes")

for file, old in PAGES.items():
    modify(file, old)
