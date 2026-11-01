/**
 * Append a message bubble to the chat history.
 * @param {string} text
 * @param {"user"|"ai"} sender
 */
function addMessage(text, sender) {
    const chatWindow = document.querySelector(".chat-window");

    let bubble = document.createElement("div");
    bubble.classList.add("chat-bubble");

    // If it's an AI message, parse markdown.
    if (sender === "ai") {
        bubble.classList.add("chat-bubble--ai");
        bubble.innerHTML = marked.parse(text);
    } else {
        bubble.classList.add("chat-bubble--user");
        bubble.innerText = text;
    }

    chatWindow.appendChild(bubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

/**
 * Send the current input to the chat API.
 */
function sendMessage() {
    const input = document.querySelector(".chat-input");
    let msg = input.value.trim();
    if (!msg) return;

    addMessage(msg, "user");
    input.value = "";

    addMessage("Typing...", "ai");
    const typingBubble = document.querySelector(".chat-bubble--ai:last-child");

    fetch("/api/chat/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "message=" + encodeURIComponent(msg)
    })
    .then(r => r.json())
    .then(data => {
        typingBubble.remove();
        addMessage(data.response, "ai");
    })
    .catch(err => {
        console.error("Fetch error:", err);
        typingBubble.remove();
        addMessage("Error connecting to server.", "ai");
    });
}

/**
 * Initialize chat interactions for the current view.
 */
function initChat() {
    const sendBtn = document.querySelector(".chat-send");
    const input = document.querySelector(".chat-input");
    const chatWindow = document.querySelector(".chat-window");

    if (!sendBtn || !input || !chatWindow) return;

    // Convert any pre-rendered messages with Markdown.
    const messages = document.querySelectorAll('.chat-parsed');
    messages.forEach(message => {
        message.innerHTML = marked.parse(message.innerHTML);
    });

    chatWindow.scrollTop = chatWindow.scrollHeight;
    requestAnimationFrame(() => {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    });
    setTimeout(() => {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }, 200);

    // Event listeners.
    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}


/**
 * Bind quick prompt buttons for the chat header.
 */
function initPromptBubbles() {
    const chatInput = document.querySelector('.chat-input');
    const quickPromptsContainer = document.querySelector('.chat-prompts');

    if (!chatInput || !quickPromptsContainer) return;

    // Use event delegation - attach ONE listener to the parent
    quickPromptsContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('chat-prompt')) {
            const promptText = e.target.getAttribute('data-prompt');
            chatInput.value = promptText;
            chatInput.focus();

            // Visual feedback
            e.target.style.opacity = '0.5';
            setTimeout(() => {
                e.target.style.opacity = '1';
            }, 200);
        }
    });
}

/**
 * Initialize chat after dynamic dashboard loads.
 */
function tryInit() {
    initChat();
    initPromptBubbles();
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', tryInit);

// Dashboard view registry calls initChat/initPromptBubbles after view load.

