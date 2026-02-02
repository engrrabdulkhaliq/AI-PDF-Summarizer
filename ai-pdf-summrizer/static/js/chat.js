const fileUpload = document.getElementById('fileUpload');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const uploadForm = document.getElementById('uploadForm');
const submitBtn = document.getElementById('submitBtn');
const errorMessage = document.getElementById('errorMessage');
const emptyState = document.getElementById('emptyState');
const loadingState = document.getElementById('loadingState');
const resultsContent = document.getElementById('resultsContent');
const metadata = document.getElementById('metadata');
const summaryText = document.getElementById('summaryText');
const keyPointsContent = document.getElementById('keyPointsContent');
const keypointsTab = document.getElementById('keypointsTab');
const mindmapTab = document.getElementById('mindmapTab');
const mindmapContainer = document.getElementById('mindmapContainer');
const chatContainer = document.getElementById('chatContainer');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const copyBtn = document.getElementById('copyBtn');
const downloadBtn = document.getElementById('downloadBtn');
const convertBtn = document.getElementById('convertBtn');
const newBtn = document.getElementById('newBtn');

let currentData = null;
let currentSessionId = null;

fileUpload.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = `📄 ${file.name}`;
        fileName.style.display = 'block';
        errorMessage.classList.remove('active');
    }
});

fileUpload.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUpload.classList.add('dragover');
});

fileUpload.addEventListener('dragleave', () => {
    fileUpload.classList.remove('dragover');
});

fileUpload.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUpload.classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
        fileInput.files = e.dataTransfer.files;
        fileName.textContent = `📄 ${file.name}`;
        fileName.style.display = 'block';
        errorMessage.classList.remove('active');
    } else {
        showError('Please drop a valid PDF file');
    }
});

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!fileInput.files[0]) {
        showError('Please select a PDF file');
        return;
    }

    const formData = new FormData(uploadForm);
    formData.append('include_key_points', document.getElementById('keyPoints').checked);
    formData.append('include_mindmap', document.getElementById('mindmap').checked);
    formData.append('use_ocr', document.getElementById('useOcr').checked);

    emptyState.style.display = 'none';
    resultsContent.classList.remove('active');
    loadingState.classList.add('active');
    submitBtn.disabled = true;
    errorMessage.classList.remove('active');

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            currentData = data;
            currentSessionId = data.session_id;
            displayResults(data);
        } else {
            showError(data.error || 'An error occurred while processing the PDF');
            loadingState.classList.remove('active');
            emptyState.style.display = 'block';
        }
    } catch (error) {
        showError('Failed to process PDF. Please try again.');
        loadingState.classList.remove('active');
        emptyState.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
    }
});

function displayResults(data) {
    loadingState.classList.remove('active');
    resultsContent.classList.add('active');

    const meta = data.metadata;
    metadata.innerHTML = `
        <div class="metadata-item">📄 ${meta.page_count} pages</div>
        <div class="metadata-item">📝 ${meta.word_count.toLocaleString()} words</div>
        <div class="metadata-item">⏱️ ${meta.reading_time} min read</div>
        <div class="metadata-item">🌐 ${meta.language.charAt(0).toUpperCase() + meta.language.slice(1)}</div>
        <div class="metadata-item">👤 ${meta.audience.charAt(0).toUpperCase() + meta.audience.slice(1)}</div>
    `;

    summaryText.textContent = data.summary;

    if (data.key_points) {
        keypointsTab.style.display = 'block';
        keyPointsContent.textContent = data.key_points;
    } else {
        keypointsTab.style.display = 'none';
    }

    if (data.mindmap_data) {
        mindmapTab.style.display = 'block';
        renderMindMap(data.mindmap_data);
    } else {
        mindmapTab.style.display = 'none';
    }

    chatContainer.innerHTML = `
        <div style="text-align: center; color: var(--text-secondary); padding: 2rem;">
            Ask questions about your document...
        </div>
    `;
}

function renderMindMap(data) {
    let html = `<div class="mindmap-central">${data.central}</div>`;
    
    if (data.branches && data.branches.length > 0) {
        data.branches.forEach(branch => {
            html += `<div class="mindmap-branch">
                <div class="mindmap-branch-title">${branch.name}</div>`;
            
            if (branch.subbranches && branch.subbranches.length > 0) {
                branch.subbranches.forEach(sub => {
                    html += `<div class="mindmap-subbranch">${sub}</div>`;
                });
            }
            
            html += `</div>`;
        });
    }
    
    mindmapContainer.innerHTML = html;
}

document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
    });
});

chatSendBtn.addEventListener('click', sendChatMessage);

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
});

async function sendChatMessage() {
    const question = chatInput.value.trim();
    
    if (!question) {
        showError('Please enter a question');
        return;
    }

    if (!currentSessionId) {
        showError('Please upload a PDF first');
        return;
    }

    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'chat-message user';
    userMessageDiv.innerHTML = `<strong>You:</strong> ${escapeHtml(question)}`;
    chatContainer.appendChild(userMessageDiv);
    
    chatInput.value = '';
    chatContainer.scrollTop = chatContainer.scrollHeight;

    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message assistant';
    loadingDiv.innerHTML = '<strong>AI:</strong> Thinking...';
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                question: question
            })
        });

        const data = await response.json();
        
        loadingDiv.remove();

        if (data.success) {
            const assistantMessageDiv = document.createElement('div');
            assistantMessageDiv.className = 'chat-message assistant';
            assistantMessageDiv.innerHTML = `<strong>AI:</strong> ${escapeHtml(data.answer)}`;
            chatContainer.appendChild(assistantMessageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        } else {
            showError(data.error || 'Failed to get response');
        }
    } catch (error) {
        loadingDiv.remove();
        showError('Failed to send message. Please try again.');
    }
}

copyBtn.addEventListener('click', async () => {
    if (!currentData) {
        showError('No summary to copy');
        return;
    }

    let textToCopy = currentData.summary;
    
    if (currentData.key_points) {
        textToCopy += '\n\nKEY POINTS:\n' + currentData.key_points;
    }

    try {
        await navigator.clipboard.writeText(textToCopy);
        
        const originalHTML = copyBtn.innerHTML;
        copyBtn.innerHTML = '✅ Copied!';
        copyBtn.style.background = 'var(--success)';
        
        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
            copyBtn.style.background = '';
        }, 2000);
    } catch (error) {
        showError('Failed to copy to clipboard');
    }
});

downloadBtn.addEventListener('click', async () => {
    if (!currentData) {
        showError('No summary to download');
        return;
    }

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentData)
        });

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `summary_${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        showError('Failed to download summary');
    }
});

convertBtn.addEventListener('click', async () => {
    if (!currentSessionId) {
        showError('No document to convert');
        return;
    }

    try {
        const response = await fetch('/convert-to-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId
            })
        });

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `extracted_${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        showError('Failed to convert to text');
    }
});

newBtn.addEventListener('click', () => {
    uploadForm.reset();
    fileName.style.display = 'none';
    resultsContent.classList.remove('active');
    emptyState.style.display = 'block';
    currentData = null;
    currentSessionId = null;
    errorMessage.classList.remove('active');
    
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelector('.tab[data-tab="summary"]').classList.add('active');
    document.getElementById('summary').classList.add('active');
    
    keypointsTab.style.display = 'none';
    mindmapTab.style.display = 'none';
});

function showError(message) {
    errorMessage.textContent = `❌ ${message}`;
    errorMessage.classList.add('active');
    
    setTimeout(() => {
        errorMessage.classList.remove('active');
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

window.addEventListener('beforeunload', (e) => {
    if (currentData && !confirm('You have unsaved work. Are you sure you want to leave?')) {
        e.preventDefault();
        e.returnValue = '';
    }
});