# PrivateGateKey — shared site chrome

This site uses **one canonical header and one canonical footer** on all four content pages.

## Sources of truth
- `site-shell/header.html` — navigation, logo, ecosystem link, mobile button.
- `site-shell/footer.html` — footer columns, legal links, copyright.
- `assets/css/site-shell.css` — responsive shared design (navy/champagne).
- `assets/js/site-shell.js` — mobile menu, Escape/outside click, active link and year.

## Regenerating static HTML
Run `python scripts/sync_site_shell.py` and then `python scripts/test_site_shell.py` before committing. This stamps identical components into `index.html`, `support.html`, `privacy.html` and `products/privategatekey/index.html` so navigation remains available even if JavaScript is blocked.

Links are root-relative and work from all site sections. Nav/footer labels are localized using the page's `html[lang]`; the existing home FR/EN selector is preserved inside the hero rather than in the shared navigation. Redirect-only alias pages (`gatekey/` and `privategatekey/`) immediately redirect to canonical content and do not carry a second layout.

The source files and output are both committed to GitHub Pages. No server-side templating is required.
