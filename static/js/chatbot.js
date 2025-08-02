document.addEventListener("DOMContentLoaded", () => {
    const chatbotBtn = document.getElementById("chatbot-btn");
    const chatbotPopup = document.getElementById("chatbot-popup");
    const chatWindow = document.getElementById("chat-window");

    const responses = {
        "What can you do?": "I'm a static chatbot built for this portfolio. I can answer predefined questions!",
        "Tell me about this site": "This is a personal portfolio built using modern Python Fullstack tech.",
        "How to contact you?": "Check out the Contact section at the bottom of this page.",
        "What technologies are used?": "HTML, CSS, JS, Python (Flask), and a bit of frontend animation magic!"
    };

    chatbotBtn.addEventListener("click", () => {
        chatbotPopup.style.display = chatbotPopup.style.display === "flex" ? "none" : "flex";
        chatWindow.innerHTML = "";
    });

    const buttons = document.querySelectorAll(".chatbot-question");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            const question = btn.textContent;
            addMessage(question, 'user');

            setTimeout(() => {
                addMessage("typing...", 'bot typing');
            }, 500);

            setTimeout(() => {
                removeTyping();
                addMessage(responses[question] || "Hmm... I haven't been taught that yet.", 'bot');
            }, 1500);
        });
    });

    function addMessage(text, sender) {
        const message = document.createElement("div");
        message.classList.add("chat-message", sender);
        message.textContent = text;
        chatWindow.appendChild(message);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function removeTyping() {
        const typing = document.querySelector(".chat-message.typing");
        if (typing) typing.remove();
    }
});
