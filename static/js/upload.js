document.addEventListener("DOMContentLoaded", function () {
  // DOM elements
  const uploadForm = document.getElementById("uploadForm");
  const messageElement = document.getElementById("message");
  const logMessagesElement = document.getElementById("logMessages");
  const uploadInterface = document.getElementById("uploadInterface");
  const loadingInterface = document.getElementById("loadingInterface");
  const buttonsInterface = document.getElementById("buttonsInterface");
  const newUploadBtn = document.getElementById("newUploadBtn");
  const downloadBtn = document.getElementById("downloadBtn");

  // Unique messages array to prevent duplicate log messages
  let uniqueMessages = [];

  // Interface visibility functions
  function showInterface(interfaceElement) {
    [uploadInterface, loadingInterface, buttonsInterface].forEach((el) => {
      el.style.display = el === interfaceElement ? "block" : "none";
    });
  }

  // Initialize interface based on task status
  function initializeInterface() {
    checkTaskStatus(true);
  }

  // Event listener for new upload button
  newUploadBtn.addEventListener("click", function () {
    showInterface(uploadInterface);
    logMessagesElement.innerHTML = "";
    uniqueMessages = [];
  });

  // Handle form submission
  function handleFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(uploadForm);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);
    xhr.onload = handleXhrResponse;
    showInterface(loadingInterface);
    xhr.send(formData);
  }

  // Handle XHR response
  function handleXhrResponse() {
    if (this.status === 200) {
      const response = JSON.parse(this.responseText);
      messageElement.innerText = response.message || response.error;
      if (response.message) {
        checkTaskStatus();
      } else {
        showInterface(uploadInterface);
      }
    } else {
      messageElement.innerText = "Error uploading file";
      showInterface(uploadInterface);
    }
  }

  // Handle log messages
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

  // Check task status
  function checkTaskStatus(isInitial = false) {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/task_status", true);
    xhr.onload = function () {
      if (this.status === 200) {
        const response = JSON.parse(this.responseText);
        console.log(response);
        switch (response.state) {
          case "SUCCESS":
            messageElement.innerText =
              response.result || "File processed successfully";
            showInterface(buttonsInterface);
            updateDownloadButtonDate();
            break;
          case "FAILURE":
            messageElement.innerText = `Error: ${response.result}`;
            showInterface(uploadInterface);
            break;
          case "PROCESSING":
            messageElement.innerText = "Processing...";
            showInterface(loadingInterface);
            setTimeout(checkTaskStatus, 2000);
            break;
          case "NO_TASK":
            if (isInitial) {
              showInterface(
                isUpdatedToday ? buttonsInterface : uploadInterface
              );
            } else {
              showInterface(uploadInterface);
            }
            break;
        }
      }
    };
    xhr.send();
  }

  // Update download button date
  function updateDownloadButtonDate() {
    const today = new Date();
    const dateString = today.toISOString().split("T")[0];
    downloadBtn.textContent = `Download inventory update files (${dateString})`;
  }

  // Socket.io setup
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

  // Initialize interface
  initializeInterface();

  // Event listener for form submission
  uploadForm.addEventListener("submit", handleFormSubmit);

  // Update download button date on load
  updateDownloadButtonDate();
});
