AOS.init({ once: true, duration: 700 });

function switchLang(lang) {
  // ustaw atrybut lang na <html>, dzięki temu contact.js będzie wiedział jaki język
  document.documentElement.setAttribute("lang", lang);

  // aktualizacja treści dla wszystkich elementów z data-en / data-pl
  document.querySelectorAll('[data-en][data-pl]').forEach(el => {
    const text = el.getAttribute(`data-${lang}`) || el.getAttribute("data-en");
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
      el.placeholder = text;
    } else {
      el.textContent = text;
    }
  });

  // zaznacz aktywny przycisk
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.lang === lang) btn.classList.add('active');
  });
}

// ustawienie preferowanego języka na start
const preferredLang = navigator.language.startsWith("pl") ? "pl" : "en";
switchLang(preferredLang);

window.addEventListener("load", () => {
  document.getElementById("loader").style.display = "none";
});
