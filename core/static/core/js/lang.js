AOS.init({ once: true, duration: 700 });

function switchLang(lang) {
  document.querySelectorAll('[data-en]').forEach(el => {
    const text = el.getAttribute(`data-${lang}`) || el.getAttribute("data-en");
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
      el.placeholder = text;
    } else {
      el.textContent = text;
    }
  });

  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.lang === lang) btn.classList.add('active');
  });

  document.documentElement.lang = lang;
}

const preferredLang = navigator.language.startsWith("pl") ? "pl" : "en";
switchLang(preferredLang);

window.addEventListener("load", () => {
  document.getElementById("loader").style.display = "none";
});
