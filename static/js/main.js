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

        if (response.ok) {
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = downloadUrl;
            a.download = response.headers.get('content-disposition')?.split('filename=')[1] || 'video.mp4';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            document.body.removeChild(a);
            showStatus('Download completed!', 'success');
        } else {
            const error = await response.json();
            showStatus(error.error || 'Download failed', 'error');
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
    console.log('Status:', message, type); // Debug log
    const statusElement = document.getElementById('status');
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.className = `status ${type}`;
        statusElement.style.display = 'block';
    } else {
        console.error('Status element not found');
    }
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

// Make sure the event listener is added
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded'); // Debug log
    const downloadButton = document.getElementById('download-button');
    if (downloadButton) {
        downloadButton.addEventListener('click', downloadContent);
        console.log('Download button listener added');
    } else {
        console.error('Download button not found');
    }
});
