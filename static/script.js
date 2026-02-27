document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const chatMessages = document.getElementById("chat-messages");
  let sessionId = localStorage.getItem("bistro_session_id");

  // Show session ID in the header if it exists
  if (sessionId) {
    const statusText = document.querySelector(".agent-info p");
    if (statusText) statusText.textContent = `Online | ID: ${sessionId}`;
  }

  // Function to append a message to the chat
  function appendMessage(role, content) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", role);

    const messageContent = document.createElement("div");
    messageContent.classList.add("message-content");
    messageContent.textContent = content;

    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Function to show typing indicator
  function showTypingIndicator() {
    const loadingDiv = document.createElement("div");
    loadingDiv.classList.add("message", "assistant", "loading-msg");
    loadingDiv.innerHTML = `
            <div class="message-content">
                <div class="typing">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return loadingDiv;
  }

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to UI
    appendMessage("user", message);
    userInput.value = "";

    // Show typing indicator
    const typingIndicator = showTypingIndicator();

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId,
        }),
      });

      const data = await response.json();

      // Remove typing indicator
      typingIndicator.remove();

      if (data.response) {
        appendMessage("assistant", data.response);
        if (data.session_id) {
          sessionId = data.session_id;
          localStorage.setItem("bistro_session_id", sessionId);
          // Show session ID in the header
          const statusText = document.querySelector('.agent-info p');
          statusText.textContent = `Online | ID: ${sessionId}`;
        }
      } else if (data.error) {
        appendMessage(
          "assistant",
          "Mi dispiace, I encountered an error. Please try again later.",
        );
        console.error("API Error:", data.error);
      }
    } catch (error) {
      typingIndicator.remove();
      appendMessage(
        "assistant",
        "Connection error. Please check if the server is running.",
      );
      console.error("Fetch Error:", error);
    }
  });

  // Modal Logic
  const modalOverlay = document.getElementById("modal-overlay");
  const modalBody = document.getElementById("modal-body");
  const closeModal = document.getElementById("close-modal");

  const modalData = {
    Inquiry: {
      title: "Inquiry Guide",
      content: `
        <h3>What you can ask:</h3>
        <ul>
          <li>Menu items and ingredients</li>
          <li>Opening hours & location</li>
          <li>Dietary/allergen information</li>
          <li>Parking & accessibility</li>
        </ul>
        <h3>Current Schedule:</h3>
        <ul>
          <li>Mon–Thu: 11AM–10PM</li>
          <li>Fri–Sat: 11AM–11PM</li>
          <li>Sun: 12PM–9PM</li>
        </ul>
      `,
    },
    Support: {
      title: "Support Guide",
      content: `
        <h3>Need help? Ask about:</h3>
        <ul>
          <li>Order status (provide Order ID)</li>
          <li>Refund and cancellation policy</li>
          <li>Wait time updates</li>
          <li>Filing a feedback or complaint</li>
        </ul>
        <h3>Order Status:</h3>
        <p>Try asking "What is the status of order #BV123?"</p>
      `,
    },
    Bookings: {
      title: "Booking Guide",
      content: `
        <h3>Reservation Tips:</h3>
        <ul>
          <li>Provide date, time, and party size</li>
          <li>Parties of 6+ recommended to book 24h ahead</li>
          <li>Specify special occasions (birthdays, etc.)</li>
          <li>2-hour cancellation notice required</li>
        </ul>
        <h3>How to speak:</h3>
        <p>"I'd like to book a table for 4 tomorrow at 7 PM for a birthday celebration."</p>
      `,
    },
  };

  const openPopup = (type) => {
    const data = modalData[type];
    if (data) {
      modalBody.innerHTML = `<h2>${data.title}</h2>${data.content}`;
      modalOverlay.style.display = "flex";
      document.body.style.overflow = "hidden"; // Prevent background scroll
    }
  };

  closeModal.addEventListener("click", () => {
    modalOverlay.style.display = "none";
    document.body.style.overflow = "auto";
  });

  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) {
      modalOverlay.style.display = "none";
      document.body.style.overflow = "auto";
    }
  });

  // Handle Quick Action Buttons
  const actionButtons = document.querySelectorAll(".action-btn");
  actionButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const type = btn.querySelector("span:last-child").textContent.trim();
      openPopup(type);
      
      // Still populate input for convenience
      const msg = btn.getAttribute("data-msg");
      userInput.value = msg;
    });
  });
});
