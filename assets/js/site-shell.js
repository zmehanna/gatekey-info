/* Shared navigation behavior — presentation stays identical across all pages. */
(() => {
  const menu = document.querySelector('.pgk-shell-menu');
  const nav = document.getElementById('pgk-shell-navigation');
  if (!menu || !nav) return;
  const close = () => { nav.dataset.open='0'; menu.setAttribute('aria-expanded','false'); menu.setAttribute('aria-label','Open navigation menu'); };
  menu.addEventListener('click', () => {
    const next = nav.dataset.open !== '1';
    nav.dataset.open = next ? '1' : '0';
    menu.setAttribute('aria-expanded', String(next));
    menu.setAttribute('aria-label', next ? 'Close navigation menu' : 'Open navigation menu');
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', close));
  document.addEventListener('keydown', event => { if (event.key === 'Escape') close(); });
  document.addEventListener('click', event => { if (nav.dataset.open==='1' && !nav.contains(event.target) && !menu.contains(event.target)) close(); });
  window.addEventListener('resize', () => { if (innerWidth > 1040) close(); });
  const path = location.pathname.replace(/\/+$/, '/') || '/';
  const active = path === '/support.html' ? 'support' : path === '/privacy.html' ? 'privacy' : path.startsWith('/products/privategatekey/') ? 'roles' : 'home';
  const selected = nav.querySelector('[data-shell-link="'+active+'"]');
  if (selected) selected.setAttribute('aria-current','page');
  document.querySelectorAll('.pgk-shell-footer-bottom #year').forEach(el => {el.textContent=String(new Date().getFullYear());});
})();
