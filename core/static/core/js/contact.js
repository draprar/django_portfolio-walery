document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#contact-form");
  if (!form) return;

  const button = form.querySelector("button[type=submit]");
  const alertBox = document.querySelector("#contact-alerts");

  // helper do wyciągania komunikatu w aktualnym języku
  function getMessage(id) {
    const lang = document.documentElement.lang || "en";
    const el = document.getElementById(id);
    return el ? (el.getAttribute(`data-${lang}`) || el.getAttribute("data-en")) : "";
  }

  function showAlert(type, messageId) {
    const message = getMessage(messageId);
    alertBox.innerHTML = `
      <div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>`;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      const data = await response.json();

      if (data.success) {
        showAlert("success", "msg-success");
        form.reset();
      } else {
        showAlert("warning", "msg-fail");
      }
    } catch (err) {
      showAlert("danger", "msg-error");
    } finally {
      button.disabled = false;
      button.innerHTML = `<span data-en="Send Message" data-pl="Wyślij wiadomość">Send Message</span>`;
    }
  });
});
