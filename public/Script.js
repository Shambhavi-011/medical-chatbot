// Configuration
const API_BASE_URL = 'http://localhost:5000';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const errorToast = document.getElementById('errorToast');
const toastMessage = document.getElementById('toastMessage');
const charCount = document.getElementById('charCount');
const scrollToBottomBtn = document.getElementById('scrollToBottomBtn');
const emojiBtn = document.getElementById('emojiBtn');
const emojiPicker = document.getElementById('emojiPicker');

// Quick action buttons
const quickBtns = document.querySelectorAll('.quick-btn');

// State
let isTyping = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('🏥 Medical Chatbot Initialized');
    setupEventListeners();
    focusInput();
});

// Event Listeners
function setupEventListeners() {
    // Form submission
    chatForm.addEventListener('submit', handleSubmit);
    
    // Enter key handling
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (messageInput.value.trim()) {
                handleSubmit(e);
            }
        }
    });
    
    // Input handling
    messageInput.addEventListener('input', () => {
        autoResizeTextarea();
        updateCharCount();
    });
    
    // Quick action buttons
    quickBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const query = btn.getAttribute('data-query');
            messageInput.value = query;
            handleSubmit(new Event('submit'));
        });
    });
    
    // Scroll button
    if (scrollToBottomBtn) {
        scrollToBottomBtn.addEventListener('click', () => scrollToBottom(true));
    }
    
    // Scroll detection
    chatMessages.addEventListener('scroll', handleScroll);
    
    // Emoji picker
    if (emojiBtn && emojiPicker) {
        emojiBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            emojiPicker.classList.toggle('show');
        });

        // Add emoji to input
        emojiPicker.addEventListener('click', (e) => {
            if (e.target.tagName === 'SPAN') {
                const emoji = e.target.textContent;
                const cursorPos = messageInput.selectionStart;
                const textBefore = messageInput.value.substring(0, cursorPos);
                const textAfter = messageInput.value.substring(cursorPos);
                
                messageInput.value = textBefore + emoji + textAfter;
                messageInput.focus();
                messageInput.selectionStart = cursorPos + emoji.length;
                messageInput.selectionEnd = cursorPos + emoji.length;
                
                updateCharCount();
                emojiPicker.classList.remove('show');
            }
        });

        // Close emoji picker when clicking outside
        document.addEventListener('click', (e) => {
            if (!emojiBtn.contains(e.target) && !emojiPicker.contains(e.target)) {
                emojiPicker.classList.remove('show');
            }
        });
    }
}

// Message Handling
async function handleSubmit(e) {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message || isTyping) return;
    
    console.log('📤 Sending message:', message);
    
    // Add user message
    addMessage('user', message);
    messageInput.value = '';
    autoResizeTextarea();
    updateCharCount();
    
    // Show typing indicator
    showTyping();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📥 Received response:', data);
        
        await delay(800);
        
        hideTyping();
        addMessage('bot', data.reply);
        
    } catch (error) {
        console.error('❌ Error:', error);
        hideTyping();
        showError('Failed to connect to server. Please check if Flask is running!');
        addMessage('bot', "I'm having trouble connecting. Please make sure the server is running and try again.");
    }
    
    focusInput();
}

// Message Display
function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    if (sender === 'user') {
        avatarDiv.innerHTML = '<i class="fas fa-user"></i>';
    } else {
        avatarDiv.className = 'message-avatar medical';
        avatarDiv.innerHTML = '<i class="fas fa-user-md"></i>';
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    
    const textP = document.createElement('p');
    textP.textContent = text;
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = getCurrentTime();
    
    bubbleDiv.appendChild(textP);
    contentDiv.appendChild(bubbleDiv);
    contentDiv.appendChild(timeSpan);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom(true);
}

// Typing Indicator
function showTyping() {
    isTyping = true;
    if (typingIndicator) typingIndicator.classList.add('active');
    scrollToBottom(true);
}

function hideTyping() {
    isTyping = false;
    if (typingIndicator) typingIndicator.classList.remove('active');
}

// Scroll Functions
function scrollToBottom(smooth = true) {
    requestAnimationFrame(() => {
        setTimeout(() => {
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: smooth ? 'smooth' : 'auto'
            });
        }, 50);
    });
}

function handleScroll() {
    const isAtBottom = chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight < 100;
    
    if (scrollToBottomBtn) {
        if (isAtBottom) {
            scrollToBottomBtn.classList.remove('show');
        } else {
            scrollToBottomBtn.classList.add('show');
        }
    }
}

// Utility Functions
function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
}

function updateCharCount() {
    const count = messageInput.value.length;
    if (charCount) {
        charCount.textContent = count;
        charCount.style.color = count > 450 ? 'var(--error)' : 'var(--text-secondary)';
    }
}

function focusInput() {
    messageInput.focus();
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Toast Notifications
function showError(message) {
    if (!errorToast || !toastMessage) return;
    toastMessage.textContent = message;
    errorToast.style.background = 'var(--error)';
    errorToast.classList.add('show');
    
    setTimeout(() => {
        errorToast.classList.remove('show');
    }, 3000);
}

function showSuccess(message) {
    if (!errorToast || !toastMessage) return;
    toastMessage.textContent = message;
    errorToast.style.background = 'var(--secondary)';
    errorToast.classList.add('show');
    
    setTimeout(() => {
        errorToast.classList.remove('show');
    }, 3000);
}

console.log('✅ Medical Chatbot Script Loaded Successfully');
