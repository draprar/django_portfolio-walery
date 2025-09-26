document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#contact-form");
  if (!form) return;

  const button = form.querySelector("button[type=submit]");
  const alertBox = document.querySelector("#contact-alerts");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Sending...';

    const formData = new FormData(form);

    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value,
        },
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        showAlert("success", data.message);
        form.reset();
      } else {
        if (data.errors) {
          Object.entries(data.errors).forEach(([field, msgs]) => {
            msgs.forEach((msg) => showAlert("danger", `${field}: ${msg}`));
          });
        } else {
          showAlert("danger", data.message || "Something went wrong.");
        }
      }
    } catch (error) {
      showAlert("danger", "Server error. Please try later.");
    } finally {
      button.disabled = false;
      button.innerHTML = '<span data-en="Send Message" data-pl="Wyślij wiadomość">Send Message</span>';
    }
  });

  function showAlert(type, message) {
    if (!alertBox) return;
    const alert = document.createElement("div");
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = "alert";
    alert.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    alertBox.appendChild(alert);
  }

});
