// static/js/upload.js

// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function () {
  // Get references to DOM elements
  const uploadForm = document.getElementById("uploadForm");
  const messageElement = document.getElementById("message");
  const loadingElement = document.getElementById("loading");
  const logMessagesElement = document.getElementById("logMessages");

  const buttonsContainer = document.getElementById("buttonsContainer");

  // if passed from flask variable is_updated_today is true, show the buttons
  console.log(isUpdatedToday);
  if (isUpdatedToday === "true") {
    buttonsContainer.style.display = "block";
  } else {
    buttonsContainer.style.display = "none";
  }

  // Add event listener for form submission
  uploadForm.addEventListener("submit", handleFormSubmit);

  // Initialize Socket.IO connection
  const socket = io();
  socket.on("log_message", handleLogMessage);

  /**
   * Handle form submission
   * @param {Event} e - The submit event
   */
  function handleFormSubmit(e) {
    e.preventDefault();

    // Create FormData object from the form
    const formData = new FormData(uploadForm);

    // Create and configure XMLHttpRequest
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);
    xhr.onload = handleXhrResponse;

    // Show loading indicator
    loadingElement.style.display = "block";

    // Send the form data
    xhr.send(formData);
  }

  /**
   * Handle XMLHttpRequest response
   */
  function handleXhrResponse() {
    if (this.status === 200) {
      const response = JSON.parse(this.responseText);
      messageElement.innerText = response.message || response.error;

      if (response.message) {
        // Show download and update API buttons on successful upload
        buttonsContainer.style.display = "block";
      }
    } else {
      messageElement.innerText = "Error uploading file";
    }

    // Hide loading indicator
    loadingElement.style.display = "none";
  }

  /**
   * Handle incoming log messages from Socket.IO
   * @param {string} msg - The log message
   */
  function handleLogMessage(msg) {
    const paragraph = document.createElement("p");
    paragraph.textContent = msg;
    logMessagesElement.appendChild(paragraph);
    logMessagesElement.scrollTop = logMessagesElement.scrollHeight;
  }
});
