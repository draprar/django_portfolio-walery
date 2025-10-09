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

  if (!galleryImages.length || !lightbox || !lightboxImg || !caption) return;

  // --- Otwieranie Lightbox ---
  function openLightbox(index) {
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
  }

  // --- Zamknięcie Lightbox ---
  function closeLightbox() {
    lightbox.style.transition = "opacity 0.3s ease";
    lightbox.style.opacity = "0";
    setTimeout(() => {
      lightbox.classList.remove("active");
      document.body.style.overflow = "";
    }, 300);
  }

  // --- Otwieranie po kliknięciu miniatury ---
  galleryImages.forEach((img, index) => {
    img.addEventListener("click", () => openLightbox(index));
  });

  // --- Kliknięcie gdziekolwiek zamyka ---
  lightbox.addEventListener("click", closeLightbox);
  lightboxImg.addEventListener("click", closeLightbox);
  caption.addEventListener("click", closeLightbox);

  // --- Zamknięcie klawiszem ESC ---
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && lightbox.classList.contains("active")) {
      closeLightbox();
    }
  });
})();
