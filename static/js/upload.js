document.addEventListener("DOMContentLoaded", function () {
  const uploadForm = document.getElementById("uploadForm");
  const messageElement = document.getElementById("message");
  const loadingElement = document.getElementById("loading");
  const logMessagesElement = document.getElementById("logMessages");
  const uploadInterface = document.getElementById("uploadInterface");
  const buttonsInterface = document.getElementById("buttonsInterface");
  const newUploadBtn = document.getElementById("newUploadBtn");

  let uniqueMessages = [];

  function showUploadInterface() {
    uploadInterface.style.display = "block";
    buttonsInterface.style.display = "none";
  }

  function showButtonsInterface() {
    uploadInterface.style.display = "none";
    buttonsInterface.style.display = "block";
  }

  if (isUpdatedToday && !isProcessing) {
    showButtonsInterface();
  } else {
    showUploadInterface();
  }

  if (isProcessing) {
    loadingElement.style.display = "block";
    checkTaskStatus();
  }

  newUploadBtn.addEventListener("click", showUploadInterface);
  uploadForm.addEventListener("submit", handleFormSubmit);

  const socket = io(window.location.origin);
  socket.on("log_message", handleLogMessage);

  function handleFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(uploadForm);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);
    xhr.onload = handleXhrResponse;
    loadingElement.style.display = "block";
    xhr.send(formData);
  }

  function handleXhrResponse() {
    if (this.status === 200) {
      const response = JSON.parse(this.responseText);
      messageElement.innerText = response.message || response.error;
      if (response.message) {
        checkTaskStatus();
      } else {
        loadingElement.style.display = "none";
      }
    } else {
      messageElement.innerText = "Error uploading file";
      loadingElement.style.display = "none";
    }
  }

  function handleLogMessage(msg) {
    console.log(msg);
    if (uniqueMessages.includes(msg.text)) {
      return;
    } else {
      uniqueMessages.push(msg.text);
    }

    const alertDiv = document.createElement("div");
    alertDiv.role = "alert";

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

  function checkTaskStatus() {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/task_status", true);
    xhr.onload = function () {
      if (this.status === 200) {
        const response = JSON.parse(this.responseText);
        if (response.state === "SUCCESS") {
          messageElement.innerText =
            response.result || "File processed successfully";
          loadingElement.style.display = "none";
          showButtonsInterface();
        } else if (response.state === "FAILURE") {
          messageElement.innerText = `Error: ${response.result}`;
          loadingElement.style.display = "none";
        } else if (response.state === "PROCESSING") {
          messageElement.innerText = "Processing...";
          setTimeout(checkTaskStatus, 2000);
        } else {
          loadingElement.style.display = "none";
        }
      }
    };
    xhr.send();
  }
});
