const navbar = document.querySelector('.navbar');
const collapseEl = document.getElementById('navbarNav');
const toggler = document.querySelector('.navbar-toggler');

// collapse - Bootstrap
const bsCollapse = collapseEl
  ? bootstrap.Collapse.getOrCreateInstance(collapseEl, { toggle: false })
  : null;

// scrolled + auto-hide during scroll
window.addEventListener('scroll', () => {
  if (window.scrollY > 50) navbar.classList.add('scrolled');
  else navbar.classList.remove('scrolled');

  if (collapseEl && collapseEl.classList.contains('show')) bsCollapse.hide();
}, { passive: true });

// auto-hide - finger
window.addEventListener('touchmove', () => {
  if (collapseEl && collapseEl.classList.contains('show')) bsCollapse.hide();
}, { passive: true });

// click outside menu → close
document.addEventListener('click', (e) => {
  if (!collapseEl || !collapseEl.classList.contains('show')) return;

  const clickedInsideMenu = collapseEl.contains(e.target);
  const clickedToggler = toggler && toggler.contains(e.target);

  if (!clickedInsideMenu && !clickedToggler) bsCollapse.hide();
});
