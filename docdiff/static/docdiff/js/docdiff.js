document.addEventListener("DOMContentLoaded", () => {
  const errorBox = document.getElementById("docdiff-error");
  if (!errorBox) return;

  const key = errorBox.dataset.error;
  const lang = document.documentElement.lang || "en";

  const msgEl = document.querySelector(
    `#docdiff-messages [data-key="${key}"]`
  );

  if (!msgEl) {
      errorBox.textContent = `Error: ${key}`;
      errorBox.classList.remove("d-none");
      return;
    }

  errorBox.innerHTML =
    msgEl.getAttribute(`data-${lang}`) ||
    msgEl.getAttribute("data-en");
});
