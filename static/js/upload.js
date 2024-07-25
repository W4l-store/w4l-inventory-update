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
    // logMessagesElement.innerHTML = "";
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
  function handleLogMessages(logs) {
    logMessagesElement.innerHTML = ""; // Clear existing logs
    logs.forEach((log) => {
      // 2024-07-25 12:22:16,479 - utils.houzz - WARNING - SKUs not found in Blue System export data: 6752
      // remuve 2024-07-25 12:22:16,479 - utils.houzz -  part from logs
      log = log.split(" - ").slice(2).join(" - ");
      const alertDiv = document.createElement("div");
      alertDiv.role = "alert";
      alertDiv.className = `alert alert-${
        log.includes("ERROR")
          ? "danger"
          : log.includes("WARNING")
          ? "warning"
          : log.includes("INFO")
          ? "info"
          : "secondary"
      }`;
      alertDiv.textContent = log;
      logMessagesElement.appendChild(alertDiv);
    });
    logMessagesElement.scrollTop = logMessagesElement.scrollHeight;
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
            handleLogMessages(response.logs);
            break;
          case "FAILURE":
            messageElement.innerText = `Error: ${response.result}`;
            showInterface(uploadInterface);
            handleLogMessages(response.logs);
            break;
          case "PROCESSING":
            messageElement.innerText = "Processing...";
            showInterface(loadingInterface);
            handleLogMessages(response.logs);
            setTimeout(checkTaskStatus, 2000);
            break;
          case "NO_TASK":
            if (isInitial) {
              if (isUpdatedToday) {
                showInterface(buttonsInterface);
                handleLogMessages(response.logs);
              } else {
                showInterface(uploadInterface);
              }
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

  // Scroll to top functionality
  const scrollToTopBtn = document.getElementById("scrollToTopBtn");

  window.addEventListener("scroll", function () {
    if (window.pageYOffset > 100) {
      scrollToTopBtn.style.display = "block";
    } else {
      scrollToTopBtn.style.display = "none";
    }
  });

  scrollToTopBtn.addEventListener("click", function () {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });

  // Initialize interface
  initializeInterface();

  // Event listener for form submission
  uploadForm.addEventListener("submit", handleFormSubmit);

  // Update download button date on load
  updateDownloadButtonDate();
});
