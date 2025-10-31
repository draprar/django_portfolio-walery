AOS.init({ once: true, duration: 700 });

function switchLang(lang) {
  document.documentElement.setAttribute("lang", lang);

  // update content for all elements with data-en / data-pl
  document.querySelectorAll('[data-en][data-pl]').forEach(el => {
    const text = el.getAttribute(`data-${lang}`) || el.getAttribute("data-en");
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
      el.placeholder = text;
    } else {
      el.textContent = text;
    }
  });

  // mark the active button
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.lang === lang) btn.classList.add('active');
  });
}

// set default language to English on start
const preferredLang = "en";
switchLang(preferredLang);

window.addEventListener("load", () => {
  document.getElementById("loader").style.display = "none";
});
