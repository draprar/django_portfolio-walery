// TWO CANVASES: left = binary matrix stream with trail, right = art-style mono symbols
(() => {
    // Canvas elements
    const leftCanvas = document.getElementById("matrixCanvas");
    const rightCanvas = document.getElementById("glitchCanvas");

    // Abort safely if matrix is not present on this page
    if (!leftCanvas || !rightCanvas) {
      // Script loaded globally, but matrix not used here
      // Exit without errors
      return;
    }

    const leftCtx = leftCanvas.getContext("2d");
    const rightCtx = rightCanvas.getContext("2d");
    const leftContainer = leftCanvas.parentElement;
    const rightContainer = rightCanvas.parentElement;

    // ----- CONFIG -----
    const pageBackgroundColor = "#0f0f0f"; // page background hex
    const glyphColor = "#888888";          // glyph color
    const fadeAlpha = 0.05;                // trail strength
    // --------------------------------------------------

    // Font sizes (density)
    const fontSizeLeft = 16;
    const fontSizeRight = 18;

    // Matrix column counters and rain drops
    let columnsLeft = 0;
    let dropsLeft = [];
    let columnsRight = 0;
    let dropsRight = [];

    // Left side uses binary stream
    const lettersLeft = "01".split("");

    // Right side uses mono-friendly unicode symbols
    const lettersRight = [
      "🔧","🔩","🏭","⚙️","🔌",
      "🐍","💻","⌨️","🧠",
      "📊","📈","📉","📑","🤖",
      "📝","📘","📄","📂",
      "🎨","✏️","🖌️","🧩","✒️"
    ];

    // Toggles
    let matrixEnabled = true;
    let glitchEnabled = false;

    // Utility: convert hex to rgba
    function hexToRgba(hex, alpha = 1) {
      let h = hex.replace("#", "");
      if (h.length === 3) {
        h = h.split("").map(ch => ch + ch).join("");
      }
      const intVal = parseInt(h, 16);
      const r = (intVal >> 16) & 255;
      const g = (intVal >> 8) & 255;
      const b = intVal & 255;
      return `rgba(${r},${g},${b},${alpha})`;
    }

    const fadeColor = hexToRgba(pageBackgroundColor, fadeAlpha);
    const glyphFill = glyphColor;

    // Resize canvases
    function resizeAll() {
      // LEFT
      leftCanvas.width = leftContainer.offsetWidth;
      leftCanvas.height = leftContainer.offsetHeight;
      columnsLeft = Math.max(1, Math.floor(leftCanvas.width / fontSizeLeft));
      dropsLeft = Array(columnsLeft).fill(1);

      // RIGHT
      rightCanvas.width = rightContainer.offsetWidth;
      rightCanvas.height = rightContainer.offsetHeight;
      columnsRight = Math.max(1, Math.floor(rightCanvas.width / fontSizeRight));
      dropsRight = Array.from(
        { length: columnsRight },
        () => -Math.floor(Math.random() * 100)
      );
    }

    // Debounced resize
    window.addEventListener("resize", () => {
      clearTimeout(window._matrixResizeTimeout);
      window._matrixResizeTimeout = setTimeout(resizeAll, 120);
    });

    document.addEventListener("DOMContentLoaded", resizeAll);
    resizeAll(); // safety run

    // LEFT MATRIX
    function drawMatrix() {
      if (!matrixEnabled) return;

      leftCtx.fillStyle = fadeColor;
      leftCtx.fillRect(0, 0, leftCanvas.width, leftCanvas.height);

      leftCtx.fillStyle = glyphFill;
      leftCtx.font = `${fontSizeLeft}px monospace`;
      leftCtx.textBaseline = "top";

      dropsLeft.forEach((y, i) => {
        const text = lettersLeft[Math.floor(Math.random() * lettersLeft.length)];
        leftCtx.fillText(text, i * fontSizeLeft, (y - 1) * fontSizeLeft);

        if (y * fontSizeLeft > leftCanvas.height && Math.random() > 0.975) {
          dropsLeft[i] = 0;
        }
        dropsLeft[i]++;
      });
    }

    // RIGHT ART MATRIX
    function drawArtMatrix() {
      if (!glitchEnabled) return;

      rightCtx.clearRect(0, 0, rightCanvas.width, rightCanvas.height);

      rightCtx.fillStyle = "#f8f9fa";
      rightCtx.font = `${fontSizeRight}px monospace`;
      rightCtx.textBaseline = "top";

      dropsRight.forEach((y, i) => {
        const text = lettersRight[Math.floor(Math.random() * lettersRight.length)];
        rightCtx.fillText(text, i * fontSizeRight, (y - 1) * fontSizeRight);

        if (y * fontSizeRight > rightCanvas.height && Math.random() > 0.975) {
          dropsRight[i] = 0;
        }
        dropsRight[i]++;
      });
    }

    // Toggle on click
    document.addEventListener("click", () => {
      matrixEnabled = !matrixEnabled;
      glitchEnabled = !matrixEnabled;

      if (!matrixEnabled) {
        leftCtx.clearRect(0, 0, leftCanvas.width, leftCanvas.height);
        dropsLeft = Array(columnsLeft).fill(1);
      }

      if (!glitchEnabled) {
        rightCtx.clearRect(0, 0, rightCanvas.width, rightCanvas.height);
        dropsRight = Array(columnsRight).fill(1);
      }
    });

    // Main loop (~30 FPS)
    setInterval(() => {
      drawMatrix();
      drawArtMatrix();
    }, 33);
})();