from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
FILES=[
 ("portail","Portail","Gate","Accès et commande sécurisée","Secure gate access and control"),
 ("aide","Aide & assistance","Help & support","Consignes et accompagnement","Safety guidance and help"),
 ("plus","Compte et accès","Account & access","Comptes, profils et autorisations","Accounts, profiles and permissions"),
 ("invites","Gestion des invités","Guest management","Invitations et utilisateurs","Invitations and users"),
 ("parametres","Paramètres & sécurité","Settings & security","Réglages et protection du portail","Preferences and gate safeguards"),
]
for slug,*_ in FILES:
    img=ROOT/"assets"/"screenshots"/f"pgk-20261118-{slug}.jpg"
    assert img.is_file() and img.stat().st_size > 25000, f"Missing {img}"
src=ROOT/"index.html"
html=src.read_text(encoding="utf-8")
assert html.count('class="showcase" aria-label="PrivateGateKey secure access visual"')==1
hero=r"""<div class="showcase pgk-hero-screenshot" aria-label="Capture réelle de l'application PrivateGateKey">
  <div class="halo" aria-hidden="true"></div>
  <a class="pgk-hero-phone" href="/assets/screenshots/pgk-20261118-portail.jpg" target="_blank" rel="noopener" aria-label="Agrandir la capture de l'écran Portail PrivateGateKey">
    <img src="/assets/screenshots/pgk-20261118-portail.jpg" alt="PrivateGateKey, écran Portail réel sur iPhone, accès privé et sécurisé" width="738" height="1600" fetchpriority="high">
  </a>
  <span class="hero-screen-label"><span class="fr">Capture réelle de l'application iPhone</span><span class="en">Real iPhone app screenshot</span></span>
</div>"""
html,changed=re.subn(r'<div class="showcase" aria-label="PrivateGateKey secure access visual">[\s\S]*?</div>(?=</div></section>)',lambda _:hero,html,count=1)
assert changed==1, "Hero screenshot replacement failed"
def home_card(slug,fr,en,detail_fr,detail_en,n):
    name=f"/assets/screenshots/pgk-20261118-{slug}.jpg"
    return f'''<figure class="pgk-shot-card">
  <a class="pgk-shot-image" href="{name}" target="_blank" rel="noopener" aria-label="Agrandir : {fr}">
    <img src="{name}" alt="Capture PrivateGateKey sur iPhone : {fr}, thème sombre" width="738" height="1600" loading="lazy" decoding="async">
  </a>
  <figcaption><span class="pgk-shot-index">{n:02d} / 05</span><strong><span class="fr">{fr}</span><span class="en">{en}</span></strong>
  <small><span class="fr">{detail_fr}</span><span class="en">{detail_en}</span></small></figcaption>
</figure>'''
items="\n".join(home_card(*row,i+1) for i,row in enumerate(FILES))
gallery=f'''<section class="section screens-section" id="screenshots">
  <div class="wrap">
    <div class="center">
      <div class="eyebrow"><span class="fr">L'expérience PrivateGateKey</span><span class="en">Inside PrivateGateKey</span></div>
      <h2><span class="fr">Découvrez la véritable application.</span><span class="en">Explore the real PrivateGateKey app.</span></h2>
      <p class="screens-lead"><span class="fr">Cinq captures récentes de PrivateGateKey sur iPhone : du portail à l'assistance, jusqu'à la gestion des invités.</span><span class="en">Five recent iPhone screenshots of PrivateGateKey, from secure gate access to support and guest management.</span></p>
    </div>
    <div class="pgk-shots-grid" aria-label="Captures d'écran de l'application PrivateGateKey">
{items}
    </div>
    <p class="pgk-shot-note"><span class="fr">Captures réelles de l'application iPhone. Touchez une image pour l'agrandir. Les écrans peuvent évoluer avec les versions.</span><span class="en">Authentic iPhone screenshots. Select an image to enlarge it. Screens may evolve with future versions.</span></p>
  </div>
</section>'''
html,changed=re.subn(r'<section class="section screens-section" id="screenshots">[\s\S]*?</section>',lambda _:gallery,html,count=1)
assert changed==1, "Home gallery replacement failed"
# Remove the dead original screenshot tab controller from the former 8-screenshot gallery.
html,dead=re.subn(r'\n\(function\(\)\{\s*const gallery=document.querySelector\(\x27\.screens-gallery\x27\);[\s\S]*?\n\}\)\(\);', '',html,count=1)
assert dead==1, "Legacy gallery JS not found"
css=r"""
/* Latest authentic iPhone screenshots — neutral PrivateGateKey identity */
.pgk-hero-screenshot{position:relative;min-height:580px}
.pgk-hero-phone{display:block;position:relative;z-index:2;width:min(260px,75%);border:6px solid #536172;border-radius:38px;overflow:hidden;background:#0c192b;box-shadow:26px 35px 80px #0009,0 0 0 1px #e3c18b60;transform:rotate(-4deg);transition:transform .2s ease}
.pgk-hero-phone:hover{transform:rotate(-2deg) translateY(-6px)}
.pgk-hero-phone img{display:block;width:100%;height:auto;aspect-ratio:738/1600;object-fit:cover}
.pgk-hero-screenshot .hero-screen-label{position:absolute;bottom:0;right:0;z-index:3;font-size:11px;padding:12px 15px;max-width:210px;background:#15283cdd;color:#e9d1a8;border-radius:14px;border:1px solid #d7b98a70}
.pgk-shots-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18px;align-items:start;margin:43px 0 0}
.pgk-shot-card{min-width:0;margin:0;padding:11px;border:1px solid rgba(220,186,129,.31);border-radius:22px;background:linear-gradient(170deg,rgba(43,62,84,.8),rgba(19,33,52,.94));box-shadow:0 18px 42px #0003;transition:transform .2s,border-color .2s}
.pgk-shot-card:hover{transform:translateY(-4px);border-color:#e7c991a8}
.pgk-shot-image{display:block;border-radius:15px;overflow:hidden;background:#071427;outline-offset:5px}
.pgk-shot-image img{display:block;width:100%;height:auto;aspect-ratio:738/1600;object-fit:contain}
.pgk-shot-card figcaption{padding:18px 7px 12px;display:flex;flex-direction:column;gap:6px;text-align:left}
.pgk-shot-index{color:#d4ad72;font-weight:700;font-size:10px;letter-spacing:.14em}
.pgk-shot-card strong{font-size:15px;font-weight:650;color:#f7f3eb;line-height:1.3}
.pgk-shot-card small{font-size:11px;line-height:1.5;color:#b6c5d5}
.pgk-shot-note{text-align:center;margin:28px auto 0;font-size:12px;line-height:1.8;color:#a5b3c0}
@media(max-width:1030px){.pgk-shots-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.pgk-shot-card{max-width:330px}}
@media(max-width:760px){.pgk-hero-screenshot{min-height:530px}.pgk-hero-phone{width:min(230px,71%);border-width:5px;border-radius:30px}.pgk-shots-grid{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(210px,71vw);grid-template-columns:none;overflow-x:auto;overscroll-behavior-inline:contain;scroll-snap-type:x mandatory;scroll-padding:20px;padding:7px 4px 23px;gap:14px;scrollbar-width:thin}.pgk-shot-card{width:100%;scroll-snap-align:start}.pgk-shot-card figcaption{padding:12px 5px 8px}.pgk-shot-note{margin-top:11px}}
@media(prefers-reduced-motion:reduce){.pgk-hero-phone,.pgk-shot-card{transition:none}}
"""
assert html.count('</style>')==1
html=html.replace('</style>',css+'</style>',1)
src.write_text(html,encoding="utf-8")
print("Home updated",src,len(html),"bytes",5,"screen cards")

prod=ROOT/"products"/"privategatekey"/"index.html"
html=prod.read_text(encoding="utf-8")
def product_card(slug,fr,en,detail_fr,detail_en,n):
    name=f"/assets/screenshots/pgk-20261118-{slug}.jpg"
    return f'''<figure class="pgk-product-shot">
  <a href="{name}" target="_blank" rel="noopener" aria-label="View PrivateGateKey {en} screenshot">
    <img src="{name}" width="738" height="1600" loading="lazy" decoding="async" alt="Actual PrivateGateKey iPhone app screen — {en}">
  </a>
  <figcaption><span class="pgk-product-shot-number">{n:02d} / 05</span><strong>{en}</strong><small>{detail_en}</small></figcaption>
</figure>'''
product_items="\n".join(product_card(*row,i+1) for i,row in enumerate(FILES))
section=f'''<section class="privategatekey-gallery" id="app-screens">
  <div class="container">
    <div class="privategatekey-centered-head">
      <span class="privategatekey-eyebrow">REAL IPHONE APP SCREENS</span>
      <h2>PrivateGateKey, as it really looks.</h2>
      <p>Explore five genuine screenshots of the latest app experience: secure gate access, help, account preferences and guest management.</p>
    </div>
    <div class="pgk-product-shots">
{product_items}
    </div>
    <p class="privategatekey-gallery-note">Actual iPhone screenshots. Select an image to see it full size. Screens may evolve with future updates.</p>
  </div>
</section>'''
html,changed=re.subn(r'<section class="privategatekey-gallery">[\s\S]*?</section>',lambda _:section,html,count=1)
assert changed==1, "Product gallery update failed"
prod.write_text(html,encoding="utf-8")
print("Product page updated",prod,len(html),"bytes")

css_file=ROOT/"assets"/"css"/"privategatekey.css"
styles=css_file.read_text(encoding="utf-8")
css_new=r"""
/* The same authentic screenshots as on the main PrivateGateKey landing page. */
.pgk-product-shots{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18px;align-items:start}
.pgk-product-shot{min-width:0;margin:0;overflow:hidden;border:1px solid #d9e1ea;border-radius:21px;background:#fff;box-shadow:0 16px 38px #0f203518}
.pgk-product-shot>a{display:block;padding:10px;background:linear-gradient(155deg,#101e32,#243950)}
.pgk-product-shot img{display:block;width:100%;height:auto;aspect-ratio:738/1600;object-fit:contain;border-radius:12px}
.pgk-product-shot figcaption{display:flex;flex-direction:column;gap:6px;padding:16px 14px 20px}
.pgk-product-shot-number{color:#a67d3c;font-size:10px;font-weight:850;letter-spacing:.15em}
.pgk-product-shot figcaption strong{font-size:14px;color:#10213b;line-height:1.3}
.pgk-product-shot figcaption small{color:#657486;font-size:11px;line-height:1.6}
@media(max-width:1100px){.pgk-product-shots{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:640px){.pgk-product-shots{grid-template-columns:none;grid-auto-flow:column;grid-auto-columns:minmax(220px,72vw);overflow-x:auto;scroll-snap-type:x mandatory;gap:14px;padding:3px 1px 18px;scrollbar-width:thin}.pgk-product-shot{scroll-snap-align:start}.pgk-product-shot figcaption{padding:13px}}
"""
assert ".pgk-product-shots" not in styles, "Product CSS already updated"
css_file.write_text(styles+"\n"+css_new,encoding="utf-8")
print("Product CSS updated")
