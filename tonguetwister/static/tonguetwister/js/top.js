// Get the button element that will scroll the user to the top of the page
const mybutton = document.getElementById("topBtn");

/**
 * Handle the window's scroll event
 * This function will check the vertical scroll position (pageYOffset) of the page.
 * If the user has scrolled down more than 1px, the button becomes visible.
 * If the user scrolls back to the top, the button is hidden.
 */
window.onscroll = () => {
  // Check if the user has scrolled more than 1px down
  if (window.pageYOffset > 1) {
    myButton.style.display = "block"; // Show the button
  } else {
    myButton.style.display = "none"; // Hide the button
  }
};

/**
 * Scroll to the top of the page with a smooth animation, when the user clicks the "top" button.
 */
const topFunction = () => {
  window.scrollTo({ top: 0, behavior: 'smooth'})
};