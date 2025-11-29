AOS.init({ once: true, duration: 700 });

(function () {
  // helpery
  const setDocumentLang = (lang) => {
    document.documentElement.setAttribute('lang', lang);
  };

  function applyTextToElement(el, text) {
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      // jeśli to placeholder/value
      if ('placeholder' in el) el.placeholder = text;
      if ('value' in el && (el.type === 'button' || el.type === 'submit')) el.value = text;
      return;
    }

    // elementy linków, nagłówków, paragrafów itp. — używamy innerHTML, bo atrybut może zawierać HTML
    el.innerHTML = text;
  }

  function switchLang(lang) {
    if (!lang) return;
    setDocumentLang(lang);

    // wszystkie elementy z obydwoma atrybutami
    document.querySelectorAll('[data-en][data-pl]').forEach(el => {
      const text = el.getAttribute(`data-${lang}`) || el.getAttribute('data-en') || '';
      applyTextToElement(el, text);
    });

    // oznacz aktywny przycisk (wszystkie .lang-btn)
    document.querySelectorAll('.lang-btn').forEach(btn => {
      const isActive = btn.dataset.lang === lang;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });

    // zapamiętanie wyboru
    try { localStorage.setItem('site_lang', lang); } catch (e) { /* ignore */ }
  }

  // podłączenie przycisków (zgodne z CSP)
  function bindLangButtons() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
      // usuwamy potencjalne inline onclick (na wszelki wypadek)
      btn.removeAttribute('onclick');

      btn.addEventListener('click', (e) => {
        const lang = btn.dataset.lang;
        switchLang(lang);
      }, { passive: true });
    });
  }

  // inicjalizacja: preferencje -> saved -> browser -> fallback 'en'
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

  // exec when DOM ready — script is deferred but extra safety
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // expose for manual testing in console if needed
  window.switchLang = switchLang;
})();
