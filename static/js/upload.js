document.addEventListener("DOMContentLoaded", function () {
  const uploadForm = document.getElementById("uploadForm");
  const messageElement = document.getElementById("message");
  const logMessagesElement = document.getElementById("logMessages");
  const uploadInterface = document.getElementById("uploadInterface");
  const loadingInterface = document.getElementById("loadingInterface");
  const buttonsInterface = document.getElementById("buttonsInterface");
  const newUploadBtn = document.getElementById("newUploadBtn");
  const downloadBtn = document.getElementById("downloadBtn");

  function showUploadInterface() {
    uploadInterface.style.display = "block";
    loadingInterface.style.display = "none";
    buttonsInterface.style.display = "none";
  }

  function showLoadingInterface() {
    uploadInterface.style.display = "none";
    loadingInterface.style.display = "block";
    buttonsInterface.style.display = "none";
  }

  function showButtonsInterface() {
    uploadInterface.style.display = "none";
    loadingInterface.style.display = "none";
    buttonsInterface.style.display = "block";
  }

  function initializeInterface() {
    checkTaskStatus(true);
  }

  newUploadBtn.addEventListener("click", function () {
    showUploadInterface();
    logMessagesElement.innerHTML = "";
    uniqueMessages = [];
  });

  function handleFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(uploadForm);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);
    xhr.onload = handleXhrResponse;
    showLoadingInterface();
    xhr.send(formData);
  }

  function handleXhrResponse() {
    if (this.status === 200) {
      const response = JSON.parse(this.responseText);
      messageElement.innerText = response.message || response.error;
      if (response.message) {
        checkTaskStatus();
      } else {
        showUploadInterface();
      }
    } else {
      messageElement.innerText = "Error uploading file";
      showUploadInterface();
    }
  }

  function handleLogMessage(msg) {
    if (!uniqueMessages.includes(msg.text)) {
      uniqueMessages.push(msg.text);
      const alertDiv = document.createElement("div");
      alertDiv.role = "alert";
      alertDiv.className = `alert alert-${
        msg.type === "error"
          ? "danger"
          : msg.type === "warning"
          ? "warning"
          : msg.type === "info"
          ? "info"
          : "secondary"
      }`;
      alertDiv.textContent = msg.text;
      logMessagesElement.appendChild(alertDiv);
      logMessagesElement.scrollTop = logMessagesElement.scrollHeight;
    }
  }

  function checkTaskStatus(isInitial = false) {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/task_status", true);
    xhr.onload = function () {
      if (this.status === 200) {
        const response = JSON.parse(this.responseText);
        switch (response.state) {
          case "SUCCESS":
            messageElement.innerText =
              response.result || "File processed successfully";
            showButtonsInterface();
            updateDownloadButtonDate();
            break;
          case "FAILURE":
            messageElement.innerText = `Error: ${response.result}`;
            showUploadInterface();
            break;
          case "PROCESSING":
            messageElement.innerText = "Processing...";
            showLoadingInterface();
            setTimeout(checkTaskStatus, 2000);
            break;
          case "NO_TASK":
            if (isInitial) {
              if (isUpdatedToday) {
                showButtonsInterface();
              } else {
                showUploadInterface();
              }
            } else {
              showUploadInterface();
            }
            break;
        }
      }
    };
    xhr.send();
  }

  function updateDownloadButtonDate() {
    const today = new Date();
    const dateString = today.toISOString().split("T")[0];
    downloadBtn.textContent = `Download inventory update files (${dateString})`;
  }

  const socket = io({
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 20000,
  });

  socket.on("disconnect", () => {
    console.log("Disconnected from server, trying to reconnect...");
  });

  socket.on("connect", () => {
    console.log("Connected to server");
  });

  socket.on("log_message", handleLogMessage);

  let uniqueMessages = [];

  initializeInterface();

  uploadForm.addEventListener("submit", handleFormSubmit);

  updateDownloadButtonDate();
});
