let isDownloading = false;

document.addEventListener('DOMContentLoaded', () => {
    const downloadBtn = document.querySelector('.download-btn');
    const urlInput = document.getElementById('url-input');
    const qualitySelect = document.getElementById('quality-select');
    const downloadProgress = document.querySelector('.download-progress');
    const progressRing = document.querySelector('.progress-ring__circle-fg');
    const progressText = document.querySelector('.progress-text');

    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => downloadContent());
    }

    if (urlInput) {
        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                downloadContent();
            }
        });
    }

    // Initialize progress ring
    if (progressRing) {
        const radius = 36;
        const circumference = radius * 2 * Math.PI;
        progressRing.style.strokeDasharray = `${circumference} ${circumference}`;
    }
});

async function downloadContent() {
    if (isDownloading) {
        showStatus('A download is already in progress', 'info');
        return;
    }

    const urlInput = document.getElementById('url-input');
    const qualitySelect = document.getElementById('quality-select');
    const downloadProgress = document.querySelector('.download-progress');
    const progressRing = document.querySelector('.progress-ring__circle-fg');
    const progressText = document.querySelector('.progress-text');

    if (!urlInput || !qualitySelect) return;

    const url = urlInput.value.trim();
    const quality = qualitySelect.value;

    if (!url) {
        showStatus('Please enter a valid URL', 'error');
        return;
    }

    try {
        isDownloading = true;
        if (downloadProgress) downloadProgress.style.display = 'flex';
        showStatus('⏳ Processing download...', 'info');

        // Reset progress indicators
        if (progressText) progressText.textContent = '0%';
        if (progressRing) progressRing.style.strokeDashoffset = progressRing.style.strokeDasharray;

        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, quality })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            // Create download link
            const a = document.createElement('a');
            a.href = `/get_file/${encodeURIComponent(data.file_path.split('\\').pop())}`;
            a.download = `${data.title}.${data.ext || 'mp4'}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            showStatus('✅ Download complete!', 'success');
            urlInput.value = '';
        } else {
            throw new Error(data.error || 'Download failed');
        }
    } catch (error) {
        console.error('Download error:', error);
        showStatus(`❌ Error: ${error.message}`, 'error');
    } finally {
        isDownloading = false;
        if (downloadProgress) downloadProgress.style.display = 'none';
    }
}

function showStatus(message, type = 'info') {
    const statusDiv = document.querySelector('.status-message') || createStatusElement();
    statusDiv.className = `status-message ${type}`;
    statusDiv.innerHTML = message;
    
    if (type !== 'info') {
        setTimeout(() => {
            statusDiv.classList.add('fade-out');
            setTimeout(() => {
                statusDiv.remove();
            }, 500);
        }, 5000);
    }
}

function createStatusElement() {
    const statusDiv = document.createElement('div');
    statusDiv.className = 'status-message';
    document.querySelector('.download-section').appendChild(statusDiv);
    return statusDiv;
}