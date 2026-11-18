from pathlib import Path
from bs4 import BeautifulSoup
import re
BASE=Path(__file__).resolve().parents[1]
labels=["portail","aide","plus","invites","parametres"]
home=BeautifulSoup((BASE/"index.html").read_text(encoding="utf-8"),"html.parser")
product=BeautifulSoup((BASE/"products/privategatekey/index.html").read_text(encoding="utf-8"),"html.parser")
for name,doc in (("home",home),("product",product)):
    assert len(doc.select(".pgk-shell-header"))==1, f"{name} shared header changed"
    assert len(doc.select(".pgk-shell-footer"))==1, f"{name} shared footer changed"
    assert len(doc.select('a[href="/support.html"]'))>=1
    assert len(doc.select('a[href="/privacy.html"]'))>=1
    cards=doc.select(".pgk-shot-card") if name=="home" else doc.select(".pgk-product-shot")
    assert len(cards)==5,(name,len(cards))
    for i,card in enumerate(cards):
        img=card.select_one("img")
        path=img["src"].lstrip("/")
        assert labels[i] in path,(name,i,path)
        assert (BASE/path).is_file(),path
        assert card.select_one("a")["href"]==img["src"]
    print("PASS",name,"5 newest screenshots in correct order")
assert home.select_one(".pgk-hero-phone img")["src"]=="/assets/screenshots/pgk-20261118-portail.jpg"
assert len(home.select(".pgk-home-locale button"))==2
assert not home.select(".screens-gallery,.screen-card,.screen-tabs")
assert not product.select(".privategatekey-gallery-grid")
for slug in labels:
    p=BASE/"assets/screenshots"/f"pgk-20261118-{slug}.jpg"
    data=p.read_bytes()
    assert data[:3]==b"\xff\xd8\xff" and data[-2:]==b"\xff\xd9",slug
    print("PASS",slug,p.stat().st_size,"bytes")
for name in ["index.html","products/privategatekey/index.html"]:
    text=(BASE/name).read_text(encoding="utf-8").lower()
    assert "maison mont-val" not in text and "maison-mont-val" not in text,name
assert (BASE/"assets/css/privategatekey.css").read_text(encoding="utf-8").count(".pgk-product-shots")>=1
print("PASS screenshots neutral, complete and correctly linked")
