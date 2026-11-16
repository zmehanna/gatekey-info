#!/usr/bin/env python3
"""Regression tests for the shared, statically rendered PrivateGateKey shell."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
PAGES=['index.html','support.html','privacy.html','products/privategatekey/index.html']
FRAGMENTS={key:(ROOT/'site-shell'/f'{key}.html').read_text(encoding='utf-8').strip() for key in ('header','footer')}
for file in PAGES:
    text=(ROOT/file).read_text(encoding='utf-8')
    for kind,fragment in FRAGMENTS.items():
        marker=f'<!-- PGK-SHARED-{kind.upper()}:START -->'
        assert text.count(marker)==1,(file,marker)
        assert text.count(fragment)==1,(file,f'{kind} differs from shared partial')
    assert text.count('/assets/css/site-shell.css')==1,(file,'missing shared css')
    assert text.count('/assets/js/site-shell.js')==1,(file,'missing shared js')
    assert text.count('id="pgk-shell-navigation"')==1,(file,'duplicate navigation')
    assert text.count('class="pgk-shell-footer"')==1,(file,'duplicate footer')
    assert text.count('id="year"')==1,(file,'duplicate year')
    assert '/assets/css/brand-site.css' not in text,(file,'obsolete design stylesheet')
    assert '/assets/js/brand-site.js' not in text,(file,'obsolete nav handler')
    if file=='index.html':
        assert text.count('data-lang="fr"')==1 and text.count('data-lang="en"')==1
        assert "document.getElementById('menu')" not in text
        assert text.count('class="pgk-home-locale"')==1
    print('PASS',file)
root=(ROOT/'index.html').read_text(encoding='utf-8')
product=(ROOT/'products/privategatekey/index.html').read_text(encoding='utf-8')
assert 'id="screenshots"' in root and 'id="features"' in root
assert 'id="roles"' in product
assert (ROOT/'assets/img/privategatekey-icon.png').exists()
assert (ROOT/'assets/css/site-shell.css').exists()
assert (ROOT/'assets/js/site-shell.js').exists()
print('PASS cross-page links and assets')
