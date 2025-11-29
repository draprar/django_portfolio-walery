const navbar = document.querySelector('.navbar');
const collapseEl = document.getElementById('navbarNav');
const toggler = document.querySelector('.navbar-toggler');

// instancja collapse Bootstrapa
const bsCollapse = collapseEl
  ? bootstrap.Collapse.getOrCreateInstance(collapseEl, { toggle: false })
  : null;

// efekt scrolled + auto-hide przy scrollu
window.addEventListener('scroll', () => {
  if (window.scrollY > 50) navbar.classList.add('scrolled');
  else navbar.classList.remove('scrolled');

  if (collapseEl && collapseEl.classList.contains('show')) bsCollapse.hide();
}, { passive: true });

// auto-hide przy przewijaniu palcem
window.addEventListener('touchmove', () => {
  if (collapseEl && collapseEl.classList.contains('show')) bsCollapse.hide();
}, { passive: true });

// kliknięcie poza menu → zamknięcie
document.addEventListener('click', (e) => {
  if (!collapseEl || !collapseEl.classList.contains('show')) return;

  const clickedInsideMenu = collapseEl.contains(e.target);
  const clickedToggler = toggler && toggler.contains(e.target);

  // jeśli kliknięto coś innego niż menu lub toggler → chowamy
  if (!clickedInsideMenu && !clickedToggler) bsCollapse.hide();
});
