// TWO CANVASES: left = binary matrix stream with trail, right = art-style mono symbols
// Comments and variable names in English

// Canvas elements
const leftCanvas = document.getElementById("matrixCanvas");
const rightCanvas = document.getElementById("glitchCanvas");
const leftCtx = leftCanvas.getContext("2d");
const rightCtx = rightCanvas.getContext("2d");
const leftContainer = leftCanvas.parentElement;
const rightContainer = rightCanvas.parentElement;

// ----- CONFIG: tune these to match your design -----
const pageBackgroundColor = "#0f0f0f"; // <-- IMPORTANT: set this to your page background hex
const glyphColor = "#888888";          // glyph color for both sides (must match your design)
const fadeAlpha = 0.05;                // how strong the trail fade is (0 = no fade, 1 = full overwrite)
// --------------------------------------------------

// Font sizes (density)
const fontSizeLeft = 16;
const fontSizeRight = 18;

// Matrix column counters and rain drops
let columnsLeft = 0;
let dropsLeft = [];
let columnsRight = 0;
let dropsRight = [];

// Left side uses binary stream like the original
const lettersLeft = "01".split("");

// Right side uses monospaced-friendly unicode symbols (monochrome & colorable)
const lettersRight = [
    // Engineering / Production
    "🔧","🔩","🏭","⚙️","🔌",

    // Programming & Python
    "🐍","💻","⌨️","🧠",

    // Data / ML / Analysis
    "📊","📈","📉","📑","🤖",

    // Documentation / Standards / Reports
    "📝","📘","📄","📂",

    // Creativity & Design
    "🎨","✏️","🖌️","🧩","✒️"
];


// Toggles – only one side active at a time
let matrixEnabled = true;
let glitchEnabled = false;

// Utility: convert hex to rgba string with given alpha
function hexToRgba(hex, alpha = 1) {
  // Accepts #rgb, #rrggbb or without '#'
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

// Precompute fade color (background color with alpha) and glyph color
const fadeColor = hexToRgba(pageBackgroundColor, fadeAlpha);
const glyphFill = glyphColor; // can be same as pageBackgroundColor for "invisible outside mask" effect

// Resizes both canvases + recalculates drop columns
function resizeAll() {
  // LEFT CANVAS
  leftCanvas.width = leftContainer.offsetWidth;
  leftCanvas.height = leftContainer.offsetHeight;
  columnsLeft = Math.max(1, Math.floor(leftCanvas.width / fontSizeLeft));
  dropsLeft = Array(columnsLeft).fill(1);

  // RIGHT CANVAS
  rightCanvas.width = rightContainer.offsetWidth;
  rightCanvas.height = rightContainer.offsetHeight;
  columnsRight = Math.max(1, Math.floor(rightCanvas.width / fontSizeRight));
  dropsRight = Array.from({ length: columnsRight }, () => -Math.floor(Math.random()*100));
}

// Debounce resize for performance
window.addEventListener("resize", () => {
  clearTimeout(window._resizeTimeout);
  window._resizeTimeout = setTimeout(resizeAll, 120);
});
document.addEventListener("DOMContentLoaded", resizeAll);
resizeAll(); // safety run

// LEFT MATRIX — includes trail effect via semi-transparent background fill
function drawMatrix() {
  if (!matrixEnabled) return;

  // Fade layer: use page background color with small alpha to achieve trail,
  // instead of rgba(0,0,0,...) which caused blackening.
  leftCtx.fillStyle = fadeColor;
  leftCtx.fillRect(0, 0, leftCanvas.width, leftCanvas.height);

  leftCtx.fillStyle = glyphFill;
  leftCtx.font = `${fontSizeLeft}px monospace`;
  leftCtx.textBaseline = "top";

  dropsLeft.forEach((y, i) => {
    const text = lettersLeft[Math.floor(Math.random() * lettersLeft.length)];
    const x = i * fontSizeLeft;
    leftCtx.fillText(text, x, (y - 1) * fontSizeLeft);

    // Reset drop randomly after bottom overflow
    if ((y * fontSizeLeft) > leftCanvas.height && Math.random() > 0.975) {
      dropsLeft[i] = 0;
    }
    dropsLeft[i]++;
  });
}

// RIGHT ART MATRIX — matching fade + glyph color so symbols visually integrate
function drawArtMatrix() {
  if (!glitchEnabled) return;

  // clear so we paint only glyphs, no darkening
  rightCtx.clearRect(0,0,rightCanvas.width,rightCanvas.height);

  // CRUCIAL: same color as page background (#f8f9fa)
  rightCtx.fillStyle = "#f8f9fa";  // <-- this makes symbols visible ONLY on the face
  rightCtx.font = `${fontSizeRight}px monospace`;
  rightCtx.textBaseline = "top";

  dropsRight.forEach((y,i)=>{
    const text = lettersRight[Math.floor(Math.random()*lettersRight.length)];
    rightCtx.fillText(text, i*fontSizeRight,(y-1)*fontSizeRight);

    if((y*fontSizeRight)>rightCanvas.height && Math.random()>0.975)
        dropsRight[i]=0;
    dropsRight[i]++;
  });
}

document.addEventListener("click", ()=>{
  matrixEnabled = !matrixEnabled;
  glitchEnabled = !matrixEnabled;

  if(!matrixEnabled){
    leftCtx.clearRect(0,0,leftCanvas.width,leftCanvas.height);
    dropsLeft = Array(columnsLeft).fill(1);  // prevent bright overlay after switching
  }
  if(!glitchEnabled){
    rightCtx.clearRect(0,0,rightCanvas.width,rightCanvas.height);
    dropsRight = Array(columnsRight).fill(1);
  }
});

// Main rendering loop (~30 FPS)
setInterval(() => {
  drawMatrix();
  drawArtMatrix();
}, 33);