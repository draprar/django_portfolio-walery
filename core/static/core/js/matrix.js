const canvas = document.getElementById("matrixCanvas");
const ctx = canvas.getContext("2d");
const container = canvas.parentElement;

function resizeMatrix() {
  canvas.width = container.offsetWidth;
  canvas.height = container.offsetHeight;
  columns = Math.floor(canvas.width / fontSize);
  drops = Array(columns).fill(1);
}

const letters = "01".split("");
const fontSize = 16;
let columns = Math.floor(canvas.width / fontSize);
let drops = Array(columns).fill(1);

window.addEventListener("resize", () => {
  clearTimeout(window.resizeTimeout);
  window.resizeTimeout = setTimeout(resizeMatrix, 200);
});
resizeMatrix();

function drawMatrix() {
  ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#888888";
  ctx.font = fontSize + "px monospace";

  drops.forEach((y, i) => {
    const text = letters[Math.floor(Math.random() * letters.length)];
    const x = i * fontSize;
    ctx.fillText(text, x, y * fontSize);

    if (y * fontSize > canvas.height && Math.random() > 0.975) {
      drops[i] = 0;
    }
    drops[i]++;
  });
}

setInterval(drawMatrix, 33);
