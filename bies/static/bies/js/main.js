// --- Funkcja zmiany języka z fade przejściem (sekcja + footer) ---
window.switchLang = function (lang) {
  const langs = document.querySelectorAll(".lang");
  const mainPL = document.getElementById("pl");
  const mainEN = document.getElementById("en");
  const footerPL = document.getElementById("pl-footer");
  const footerEN = document.getElementById("en-footer");

  // Funkcja pomocnicza do fade przejść
  function fadeSwitch(showEl, hideEl) {
    if (!showEl || !hideEl) return;
    hideEl.style.opacity = "0";
    hideEl.classList.remove("active");
    showEl.classList.add("active");
    showEl.style.opacity = "0";
    setTimeout(() => (showEl.style.opacity = "1"), 50);
  }

  // Przełączanie treści głównej
  if (lang === "pl") fadeSwitch(mainPL, mainEN);
  else if (lang === "en") fadeSwitch(mainEN, mainPL);

  // Przełączanie footera
  if (lang === "pl") fadeSwitch(footerPL, footerEN);
  else if (lang === "en") fadeSwitch(footerEN, footerPL);
};

// --- Główna część (IIFE) ---
(function () {
  const galleryImages = Array.from(document.querySelectorAll(".gallery img"));
  const lightbox = document.getElementById("lightbox");
  const lightboxImg = document.getElementById("lightbox-img");
  const caption = document.getElementById("caption");

  if (!galleryImages.length || !lightbox || !lightboxImg) return;

  let currentIndex = 0;
  let zoom = 1;
  let isDragging = false;
  let startX, startY, scrollLeft, scrollTop;

  // --- Otwieranie Lightbox ---
  function openLightbox(index) {
    currentIndex = index;
    const img = galleryImages[index];
    lightboxImg.src = img.dataset.full || img.src;
    caption.textContent = img.alt || "";

    lightbox.classList.add("active");
    lightbox.style.opacity = "0";
    document.body.style.overflow = "hidden";

    setTimeout(() => {
      lightbox.style.transition = "opacity 0.3s ease";
      lightbox.style.opacity = "1";
    }, 10);

    zoom = 1;
    lightboxImg.style.transform = "scale(1)";
  }

  // --- Zamknięcie Lightbox ---
  function closeLightbox() {
    lightbox.style.transition = "opacity 0.3s ease";
    lightbox.style.opacity = "0";
    setTimeout(() => {
      lightbox.classList.remove("active");
      document.body.style.overflow = "";
      zoom = 1;
      lightboxImg.style.transform = "scale(1)";
    }, 300);
  }

  // --- Zmiana obrazka (strzałkami lub kliknięciem) ---
  function showNext(delta) {
    currentIndex = (currentIndex + delta + galleryImages.length) % galleryImages.length;
    openLightbox(currentIndex);
  }

  // Kliknięcie na miniaturę otwiera
  galleryImages.forEach((img, index) => {
    img.addEventListener("click", () => openLightbox(index));
  });

  // Kliknięcie gdziekolwiek w tło zamyka
  lightbox.addEventListener("click", (e) => {
    if (e.target === lightbox) closeLightbox();
  });

  // Klawisze: Esc, ←, →
  document.addEventListener("keydown", (e) => {
    if (lightbox.classList.contains("active")) {
      if (e.key === "Escape") closeLightbox();
      else if (e.key === "ArrowRight") showNext(1);
      else if (e.key === "ArrowLeft") showNext(-1);
    }
  });

  // Zoom scroll / double-click
  lightboxImg.addEventListener("wheel", (e) => {
    e.preventDefault();
    zoom += e.deltaY * -0.001;
    zoom = Math.min(Math.max(1, zoom), 4);
    lightboxImg.style.transform = `scale(${zoom})`;
  });

  lightboxImg.addEventListener("dblclick", (e) => {
    e.stopPropagation();
    zoom = zoom === 1 ? 2 : 1;
    lightboxImg.style.transform = `scale(${zoom})`;
  });

  // Dragowanie przy powiększeniu
  lightboxImg.addEventListener("mousedown", (e) => {
    if (zoom <= 1) return;
    isDragging = true;
    startX = e.pageX - lightboxImg.offsetLeft;
    startY = e.pageY - lightboxImg.offsetTop;
    scrollLeft = lightbox.scrollLeft;
    scrollTop = lightbox.scrollTop;
  });

  lightbox.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    e.preventDefault();
    const x = e.pageX - lightboxImg.offsetLeft;
    const y = e.pageY - lightboxImg.offsetTop;
    const walkX = (x - startX) * 1.5;
    const walkY = (y - startY) * 1.5;
    lightbox.scrollLeft = scrollLeft - walkX;
    lightbox.scrollTop = scrollTop - walkY;
  });

  ["mouseup", "mouseleave"].forEach((ev) =>
    lightbox.addEventListener(ev, () => (isDragging = false))
  );
})();
