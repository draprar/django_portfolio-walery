const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
const sections = Array.from(navLinks).map(link => document.querySelector(link.getAttribute('href')));

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.getAttribute('id');
      navLinks.forEach(link => {
        const isActive = link.getAttribute('href') === `#${id}`;
        link.classList.toggle('active', isActive);
        if (isActive) {
          link.setAttribute('aria-current', 'page');
        } else {
          link.removeAttribute('aria-current');
        }
      });
    }
  });
}, {
  rootMargin: '-50% 0px -40% 0px',
  threshold: 0.1
});

sections.forEach(section => {
  if (section) observer.observe(section);
});

navLinks.forEach(link => {
  link.addEventListener('click', () => {
    navLinks.forEach(l => l.classList.remove('active'));
    link.classList.add('active');
  });
});
