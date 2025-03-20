let sessionActive = true; // Since files are loaded from backend, we start with active session

// Configure marked options
marked.setOptions({
    highlight: function(code, language) {
        if (language && hljs.getLanguage(language)) {
            try {
                return hljs.highlight(code, { language }).value;
            } catch (err) {}
        }
        return code;
    },
    breaks: true,
    gfm: true
});

function addMessage(message, isUser = false) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    // Create message header
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.style.background = isUser ? 'var(--message-user-bg)' : 'var(--accent-color)';
    avatarDiv.textContent = isUser ? 'You' : 'AI';
    
    const nameSpan = document.createElement('span');
    nameSpan.textContent = isUser ? 'You' : 'Assistant';
    
    headerDiv.appendChild(avatarDiv);
    headerDiv.appendChild(nameSpan);
    messageDiv.appendChild(headerDiv);
    
    // Create message content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isUser) {
        contentDiv.textContent = message;
    } else {
        contentDiv.innerHTML = marked.parse(message);
        // Initialize syntax highlighting for code blocks
        contentDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
    
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);
    
    // Smooth scroll to bottom
    messagesDiv.scrollTo({
        top: messagesDiv.scrollHeight,
        behavior: 'smooth'
    });
}

function showTypingIndicator() {
    document.getElementById('typing-indicator').style.display = 'block';
    const messagesDiv = document.getElementById('chat-messages');
    messagesDiv.scrollTo({
        top: messagesDiv.scrollHeight,
        behavior: 'smooth'
    });
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator').style.display = 'none';
}

async function sendQuery() {
    const queryInput = document.getElementById('query-input');
    const sendButton = document.querySelector('.send-button');
    const query = queryInput.value.trim();
    
    if (!query) return;

    // Disable input while processing
    queryInput.disabled = true;
    sendButton.disabled = true;

    addMessage(query, true);
    queryInput.value = '';
    
    showTypingIndicator();

    try {
        const response = await fetch('/process-query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();
        hideTypingIndicator();
        
        if (response.ok) {
            addMessage(data.response, false);
        } else {
            addMessage(`Error: ${data.detail}`, false);
        }
    } catch (error) {
        hideTypingIndicator();
        addMessage('Error processing query: ' + error.message, false);
    } finally {
        // Re-enable input
        queryInput.disabled = false;
        sendButton.disabled = false;
        queryInput.focus();
    }
}

// Handle Enter key in input
document.getElementById('query-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendQuery();
    }
});

// Clean up when window closes
window.addEventListener('beforeunload', async () => {
    if (sessionActive) {
        try {
            await fetch('/cleanup', { method: 'POST' });
        } catch (error) {
            console.error('Error during cleanup:', error);
        }
    }
}); 