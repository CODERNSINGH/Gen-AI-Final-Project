// ──────────────────────────────────────────────────────────────────────────────
// client/app.js - Vanilla JS Logic for CBSE Tutor
// ──────────────────────────────────────────────────────────────────────────────

const BACKEND_URL = "https://gen-ai-final-project.onrender.com";

// State
let currentSubject = "All Subjects";
let isGenerating = false;

// DOM Elements
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const chatContainer = document.getElementById('chatContainer');
const emptyState = document.getElementById('emptyState');
const subjectSelect = document.getElementById('subjectSelect');
const newChatBtn = document.getElementById('newChatBtn');
const suggestionsList = document.getElementById('suggestionsList');
const statsTotal = document.getElementById('statsTotal');
const statsList = document.getElementById('statsList');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');

// Mobile sidebar elements
const sidebar = document.getElementById('sidebar');
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const sidebarOverlay = document.getElementById('sidebarOverlay');

// Examples dictionary matching streamlits's old logic
const SUBJECT_EXAMPLES = {
    "Mathematics": [
        "Prove the Pythagoras theorem with diagram",
        "Solve: 2x² − 7x + 3 = 0 using the quadratic formula",
        "Find HCF of 96 and 404 using Euclid’s algorithm",
        "Prove that √2 is irrational"
    ],
    "Science": [
        "State and explain Ohm’s Law with derivation",
        "Explain the process of photosynthesis",
        "What is the difference between mitosis and meiosis?",
        "Describe the reaction between acids and bases"
    ],
    "English": [
        "Write a formal letter to the Principal requesting leave",
        "Explain the theme of the poem Fire and Ice",
        "Write a paragraph on the importance of education",
        "What is the central idea of the chapter A Letter to God?"
    ],
    "SST": [
        "What were the causes of the French Revolution?",
        "Explain the concept of federalism in India",
        "What is sustainable development?",
        "Describe the impact of globalisation on Indian economy"
    ]
};

// Setup Markdown parser options
marked.setOptions({
    gfm: true,
    breaks: true,
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    }
});

// ──────────────────────────────────────────────────────────────────────────────
// API Polling & Boot
// ──────────────────────────────────────────────────────────────────────────────

async function checkHealth() {
    try {
        const res = await fetch(`${BACKEND_URL}/health`);
        if(res.ok) {
            statusIndicator.className = "status-indicator online";
            statusText.textContent = "Backend Connected";
        } else {
            throw new Error("Not OK");
        }
    } catch(e) {
        statusIndicator.className = "status-indicator offline";
        statusText.textContent = "Backend Offline";
    }
}

async function fetchStats() {
    try {
        const res = await fetch(`${BACKEND_URL}/stats`);
        const data = await res.json();
        const stats = data.stats || [];
        
        const total = stats.reduce((acc, curr) => acc + curr.chunks, 0);
        statsTotal.textContent = `${total.toLocaleString()} indexed chunks`;
        
        statsList.innerHTML = stats.map(s => {
            const pct = Math.round((s.chunks / total) * 100) || 0;
            return `
            <div class="stat-item">
                <div class="stat-header">
                    <span class="stat-subject">${s.subject}</span>
                    <span class="stat-count">${s.chunks.toLocaleString()}</span>
                </div>
                <div class="stat-bar-bg">
                    <div class="stat-bar-fill" style="width: ${pct}%"></div>
                </div>
            </div>`;
        }).join('');
    } catch(e) {
        statsTotal.textContent = "Indexing / Offline";
        statsList.innerHTML = "";
    }
}

// ──────────────────────────────────────────────────────────────────────────────
// UI Logic
// ──────────────────────────────────────────────────────────────────────────────

function renderSuggestions() {
    const subjForEx = currentSubject === "All Subjects" ? "Science" : currentSubject;
    const examples = SUBJECT_EXAMPLES[subjForEx] || [];
    
    suggestionsList.innerHTML = examples.map(ex => 
        `<button class="suggestion-btn" onclick="prefillAndSend('${ex.replace(/'/g, "\\'")}')">${ex}</button>`
    ).join('');
}

function prefillAndSend(txt) {
    if(window.innerWidth <= 768) toggleSidebar(false);
    chatInput.value = txt;
    handleSend();
}

// Auto-resize Textarea
chatInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    if(this.value.trim() === '') {
        sendBtn.disabled = true;
    } else {
        sendBtn.disabled = false;
    }
});

chatInput.addEventListener('keydown', function(e) {
    if(e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});

subjectSelect.addEventListener('change', (e) => {
    currentSubject = e.target.value;
    renderSuggestions();
});

newChatBtn.addEventListener('click', () => {
    // Clear chat
    document.querySelectorAll('.message-wrapper').forEach(e => e.remove());
    emptyState.style.display = 'flex';
    if(window.innerWidth <= 768) toggleSidebar(false);
});

mobileMenuBtn.addEventListener('click', () => toggleSidebar(true));
sidebarOverlay.addEventListener('click', () => toggleSidebar(false));

function toggleSidebar(show) {
    if(show) {
        sidebar.classList.add('open');
        sidebarOverlay.classList.add('open');
    } else {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('open');
    }
}

// ──────────────────────────────────────────────────────────────────────────────
// Messaging
// ──────────────────────────────────────────────────────────────────────────────

function autoScroll() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function appendUserMessage(text) {
    emptyState.style.display = 'none';
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper user';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;
    
    wrapper.appendChild(content);
    chatContainer.appendChild(wrapper);
    autoScroll();
}

function appendAIPlaceholder() {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper assistant';
    wrapper.innerHTML = `
        <div class="ai-avatar">A</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    chatContainer.appendChild(wrapper);
    autoScroll();
    return wrapper;
}

function updateAIMessage(wrapperDom, data, elapsed) {
    const rawMarkdown = data.answer || "Sorry, I could not generate an answer.";
    const cleanHtml = DOMPurify.sanitize(marked.parse(rawMarkdown));
    
    const sources = data.sources || [];
    const subject = data.subject || "";
    
    let footerHtml = "";
    if(sources.length > 0 || subject || elapsed) {
        let pills = sources.slice(0,3).map(s => `<span class="source-pill">${s}</span>`).join('');
        footerHtml = `
            <div class="message-meta">
                <div class="stats-row">
                    ${subject ? `<span>${subject}</span> • ` : ''}
                    ${elapsed ? `<span>${elapsed}s</span>` : ''}
                </div>
                ${sources.length > 0 ? `<div>Sources: ${pills}</div>` : ''}
            </div>
        `;
    }

    const contentDiv = wrapperDom.querySelector('.message-content');
    contentDiv.innerHTML = `<div class="markdown-body">${cleanHtml}</div>${footerHtml}`;
    
    autoScroll();
}

async function handleSend() {
    if(isGenerating) return;
    const text = chatInput.value.trim();
    if(!text) return;

    // Reset input
    chatInput.value = '';
    chatInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Build Payload
    const payload = {
        question: text,
        subject: currentSubject === "All Subjects" ? null : currentSubject
    };

    appendUserMessage(text);
    const aiWrapper = appendAIPlaceholder();
    isGenerating = true;

    const t0 = performance.now();
    try {
        const res = await fetch(`${BACKEND_URL}/ask`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        if(!res.ok) {
            const errBase = await res.text();
            throw new Error(`HTTP Error: ${res.status} - ${errBase}`);
        }

        const data = await res.json();
        const t1 = performance.now();
        const elapsed = ((t1 - t0)/1000).toFixed(1);

        updateAIMessage(aiWrapper, data, elapsed);

    } catch (e) {
        aiWrapper.querySelector('.message-content').innerHTML = `
            <div style="color: #ff453a;">
                <b>Error connecting to backend:</b><br/>${e.message}<br/><br/>
                <i>Make sure your FastAPI server is running on port 8000.</i>
            </div>
        `;
        autoScroll();
    } finally {
        isGenerating = false;
        sendBtn.disabled = (chatInput.value.trim() === '');
    }
}

// ──────────────────────────────────────────────────────────────────────────────
// Boot
// ──────────────────────────────────────────────────────────────────────────────
sendBtn.disabled = true;
renderSuggestions();
checkHealth();
fetchStats();
// Poll health every 15s
setInterval(checkHealth, 15000);
