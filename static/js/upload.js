// static/js/upload.js

// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function () {
  // Get references to DOM elements
  const uploadForm = document.getElementById("uploadForm");
  const messageElement = document.getElementById("message");
  const loadingElement = document.getElementById("loading");
  const logMessagesElement = document.getElementById("logMessages");

  const buttonsContainer = document.getElementById("buttonsContainer");

  const uploadInterface = document.getElementById("uploadInterface");
  const buttonsInterface = document.getElementById("buttonsInterface");
  const newUploadBtn = document.getElementById("newUploadBtn");

  let uniqueMassages = [];

  function showUploadInterface() {
    uploadInterface.style.display = "block";
    buttonsInterface.style.display = "none";
  }

  function showButtonsInterface() {
    uploadInterface.style.display = "none";
    buttonsInterface.style.display = "block";
  }

  if (isUpdatedToday) {
    showButtonsInterface();
  } else {
    showUploadInterface();
  }

  newUploadBtn.addEventListener("click", showUploadInterface);

  // Здесь нужно добавить обработчик успешной загрузки файла,
  // который будет вызывать showButtonsInterface()

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
        showButtonsInterface();
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
    // Check if this is an error message and if it's the same as the last one
    if (uniqueMassages.includes(msg.text)) {
      return;
    } else {
      uniqueMassages.push(msg.text);
    }

    const alertDiv = document.createElement("div");
    alertDiv.role = "alert";

    // Determine the alert class based on the message type
    switch (msg.type) {
      case "error":
        alertDiv.className = "alert alert-danger";

        break;
      case "warning":
        alertDiv.className = "alert alert-warning";
        break;
      case "info":
        alertDiv.className = "alert alert-info";
        break;
      default:
        alertDiv.className = "alert alert-secondary";
    }

    alertDiv.textContent = msg.text;

    logMessagesElement.appendChild(alertDiv);
    logMessagesElement.scrollTop = logMessagesElement.scrollHeight;
  }
});
