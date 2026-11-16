(() => {
const button=document.querySelector('.pgk-menu'), links=document.getElementById('pgk-links');
if(!button||!links)return;
const close=()=>{links.dataset.open='0';button.setAttribute('aria-expanded','false');button.setAttribute('aria-label','Open navigation menu')};
button.addEventListener('click',()=>{const open=links.dataset.open==='1';links.dataset.open=open?'0':'1';button.setAttribute('aria-expanded',String(!open));button.setAttribute('aria-label',open?'Open navigation menu':'Close navigation menu')});
links.querySelectorAll('a').forEach(a=>a.addEventListener('click',close));
document.addEventListener('keydown',event=>{if(event.key==='Escape')close()});
document.addEventListener('click',event=>{if(links.dataset.open==='1'&&!links.contains(event.target)&&!button.contains(event.target))close()});
window.addEventListener('resize',()=>{if(window.innerWidth>980)close()});
})();