AOS.init({ once: true, duration: 700 });

(function () {
  // helpers
  const setDocumentLang = (lang) => {
    document.documentElement.setAttribute('lang', lang);
  };

  function applyTextToElement(el, text) {
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      // if placeholder/value
      if ('placeholder' in el) el.placeholder = text;
      if ('value' in el && (el.type === 'button' || el.type === 'submit')) el.value = text;
      return;
    }

    el.innerHTML = text;
  }

  function switchLang(lang) {
    if (!lang) return;
    setDocumentLang(lang);

    // all elements with both attributes
    document.querySelectorAll('[data-en][data-pl]').forEach(el => {
      const text = el.getAttribute(`data-${lang}`) || el.getAttribute('data-en') || '';
      applyTextToElement(el, text);
    });

    // all .lang-btn
    document.querySelectorAll('.lang-btn').forEach(btn => {
      const isActive = btn.dataset.lang === lang;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });

    // save choice
    try { localStorage.setItem('site_lang', lang); } catch (e) { /* ignore */ }
  }

  // CSP buttons
  function bindLangButtons() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
      btn.removeAttribute('onclick');

      btn.addEventListener('click', (e) => {
        const lang = btn.dataset.lang;
        switchLang(lang);
      }, { passive: true });
    });
  }

  // initialization
  function init() {
    bindLangButtons();

    let lang = null;
    try { lang = localStorage.getItem('site_lang'); } catch (e) { lang = null; }

    if (!lang) {
      const nav = (navigator.languages && navigator.languages[0]) || navigator.language || navigator.userLanguage || '';
      if (nav && nav.toLowerCase().startsWith('pl')) lang = 'pl';
      else if (nav && nav.toLowerCase().startsWith('en')) lang = 'en';
      else lang = 'en';
    }

    // apply immediately
    switchLang(lang);

    // hide loader after init
    window.addEventListener('load', () => {
      const loader = document.getElementById('loader');
      if (loader) loader.style.display = 'none';
    });
  }

  // exec when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.switchLang = switchLang;
})();
