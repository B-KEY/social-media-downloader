let isDownloading = false;
let downloadHistory = [];

// Load history from localStorage on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedHistory = localStorage.getItem('downloadHistory');
    if (savedHistory) {
        downloadHistory = JSON.parse(savedHistory);
        updateHistoryDisplay();
    }
});

async function downloadContent() {
    const statusElement = document.getElementById('status');
    if (isDownloading) {
        showStatus('A download is already in progress', 'info');
        return;
    }

    const urlInput = document.getElementById('url-input');
    const url = urlInput.value.trim();

    if (!url) {
        showStatus('Please enter a valid URL', 'error');
        return;
    }

    try {
        isDownloading = true;
        showStatus('Processing URL...', 'info');

        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });

        const data = await response.json();
        
        if (data.status === 'success' && data.download_url) {
            showStatus(`Downloading: ${data.title}`, 'success');
            
            // Create a hidden download link
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = data.download_url;
            a.download = `${data.title}.${data.ext || 'mp4'}`;
            
            // Add to document, click, and remove
            document.body.appendChild(a);
            a.click();
            
            // Small delay before removal
            setTimeout(() => {
                document.body.removeChild(a);
                showStatus(`Download started: ${data.title}`, 'success');
            }, 1000);

        } else {
            showStatus(data.error || 'Download failed', 'error');
        }
    } catch (error) {
        console.error('Download error:', error);
        showStatus(`Error: ${error.message}`, 'error');
    } finally {
        isDownloading = false;
    }
}

function updateHistoryDisplay() {
    const historyList = document.getElementById('history-list');
    if (!historyList) return;

    historyList.innerHTML = downloadHistory.map(item => `
        <div class="history-item">
            <div class="history-icon">
                <i class="fab fa-${item.platform.toLowerCase()}"></i>
            </div>
            <div class="history-details">
                <div class="history-title">${item.title}</div>
                <div class="history-meta">
                    <span class="history-quality">${item.quality}</span>
                    <span class="history-time">${item.timestamp}</span>
                </div>
            </div>
        </div>
    `).join('');

    // Update localStorage when history changes
    localStorage.setItem('downloadHistory', JSON.stringify(downloadHistory));
}

function showStatus(message, type = 'info') {
    const statusElement = document.getElementById('status');
    statusElement.textContent = message;
    statusElement.className = `status ${type}`;
    statusElement.style.display = 'block';
}

const style = document.createElement('style');
style.textContent = `
.history-item {
    display: flex;
    align-items: center;
    padding: 10px;
    border-bottom: 1px solid #eee;
    transition: background-color 0.2s;
}

.history-item:hover {
    background-color: #f5f5f5;
}

.history-icon {
    font-size: 1.5em;
    margin-right: 15px;
    width: 30px;
    text-align: center;
}

.history-details {
    flex-grow: 1;
}

.history-title {
    font-weight: bold;
    margin-bottom: 5px;
}

.history-meta {
    font-size: 0.9em;
    color: #666;
}

.history-quality {
    background-color: #e9ecef;
    padding: 2px 6px;
    border-radius: 3px;
    margin-right: 10px;
}

.history-time {
    color: #999;
}
`;
document.head.appendChild(style);

// Add at the beginning of your main.js
function toggleTheme() {
    const body = document.documentElement;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme toggle icon
    const themeIcon = document.querySelector('.theme-toggle i');
    themeIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    
    // Keep particles red in both themes
    if (window.pJSDom && window.pJSDom[0]) {
        const particlesColor = '#ff0000';  // Always red
        window.pJSDom[0].pJS.particles.color.value = particlesColor;
        window.pJSDom[0].pJS.particles.line_linked.color = particlesColor;
        window.pJSDom[0].pJS.fn.particlesRefresh();
    }
}

// Update theme initialization
document.addEventListener('DOMContentLoaded', () => {
    // Set dark as default if no theme is saved
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Set correct icon (sun for dark mode)
    const themeIcon = document.querySelector('.theme-toggle i');
    themeIcon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    
    // Load download history
    const savedHistory = localStorage.getItem('downloadHistory');
    if (savedHistory) {
        downloadHistory = JSON.parse(savedHistory);
        updateHistoryDisplay();
    }
});
