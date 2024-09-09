document.getElementById("send-btn").addEventListener("click", function() {
    var userInput = document.getElementById("user-input").value;
    
    if (userInput.trim() !== "") {
        appendMessage("User", userInput);
        sendMessageToServer(userInput);
        document.getElementById("user-input").value = "";
    }
});

function appendMessage(sender, message, timestamp = null, emotion = null) {
    var chatBox = document.getElementById("chat-box");
    var messageElement = document.createElement("div");

    // Assign a class to the message element based on the sender
    if (sender === "User") {
        messageElement.className = "user-message";
    } else {
        messageElement.className = "bot-message";
        if (emotion) {
            // Adjust color based on detected emotion
            applyMood(emotion);

            if (emotion === 'joy') {
                messageElement.style.backgroundColor = "#ffe8e8";
            } else if (emotion === 'sadness') {
                messageElement.style.backgroundColor = "#2199c4";
            } else if (emotion === 'anger') {
                messageElement.style.backgroundColor = "#d95f5f";
            } else if (emotion === 'fear') {
                messageElement.style.backgroundColor = "#72e67f";
            } else if (emotion === 'love') {
                messageElement.style.backgroundColor = "#f67878";
            } else if (emotion === 'surprise') {
                messageElement.style.backgroundColor = "#de8ae1";
            }
        }
    }

    // Combine the timestamp and message into one string
    var messageContent = message;
    if (timestamp) {
        messageContent = `<span class="timestamp">[${timestamp}]</span> ${message}`;
    }

    // Set the innerHTML to include both the timestamp and the message
    messageElement.innerHTML = `${sender}: ${messageContent}`;

    chatBox.appendChild(messageElement);

    // Scroll to the bottom of the chat box
    chatBox.scrollTop = chatBox.scrollHeight;

    // If the bot's response indicates the end of the conversation, disable input
    if (message.toLowerCase().includes("come back anytime")) {
        document.getElementById("user-input").disabled = true;
        document.getElementById("send-btn").disabled = true;
        document.getElementById("input-container").disabled = true;
    }
}

function sendMessageToServer(message) {
    document.getElementById("typing-indicator").style.display = "block";

    fetch("/get_response", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: message }),
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        document.getElementById("typing-indicator").style.display = "none";
        appendMessage("Bot", data.response, data.timestamp);
    })
    .catch(function(error) {
        console.error("Error:", error);
        document.getElementById("typing-indicator").style.display = "none";
        appendMessage("Bot", "Sorry, something went wrong. Please try again.");
    });
}

// Apply mood-based class to the chat container
function applyMood(emotion) {
    var chatContainer = document.getElementById("chat-container");

    // Remove any existing mood classes
    chatContainer.classList.remove("mood-joy", "mood-sadness", "mood-anger", "mood-fear", "mood-love", "mood-surprise");

    // Add the appropriate class based on the detected emotion
    if (emotion === 'joy') {
        chatContainer.classList.add("mood-joy");
    } else if (emotion === 'sadness') {
        chatContainer.classList.add("mood-sadness");
    } else if (emotion === 'anger') {
        chatContainer.classList.add("mood-anger");
    } else if (emotion === 'fear') {
        chatContainer.classList.add("mood-fear");
    } else if (emotion === 'love') {
        chatContainer.classList.add("mood-love");
    } else if (emotion === 'surprise') {
        chatContainer.classList.add("mood-surprise");
    }
}

// Fetch and display the introduction message when the page loads
function fetchIntroMessage() {
    fetch("/get_intro", {
        method: "GET",
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        appendMessage("Bot", data.response, data.timestamp);
    })
    .catch(function(error) {
        console.error("Error:", error);
        appendMessage("Bot", "Sorry, something went wrong while loading the introduction.");
    });
}

// Call fetchIntroMessage when the page loads
window.onload = function() {
    fetchIntroMessage();
};
