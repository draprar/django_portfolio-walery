(function() {
  function switchLang(lang) {
    document.querySelectorAll('.lang').forEach(el => el.classList.remove('active'));
    document.getElementById(lang).classList.add('active');
  }

  const galleryImages = document.querySelectorAll('.gallery img');
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  const caption = document.getElementById('caption');
  const close = document.getElementById('close');

  galleryImages.forEach(img => {
    img.addEventListener('click', () => {
      lightbox.style.display = 'flex';
      lightboxImg.src = img.dataset.full || img.src;
      caption.textContent = img.alt;
    });
  });

  close.addEventListener('click', () => lightbox.style.display = 'none');
  lightbox.addEventListener('click', e => { 
    if (e.target === lightbox) lightbox.style.display = 'none'; 
  });
})();
