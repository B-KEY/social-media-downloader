let isDownloading = false;

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

        const data = await response.json();
        
        if (data.status === 'success' && data.download_url) {
            showStatus(`Starting download: ${data.title}`, 'success');
            
            // Create a hidden download link
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = data.download_url;
            a.download = `${data.title}.${data.ext}`;  // This will trigger download
            
            // Add to document and click
            document.body.appendChild(a);
            a.click();
            
            // Cleanup
            setTimeout(() => {
                document.body.removeChild(a);
                showStatus(`Download started for: ${data.title}`, 'success');
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

function showStatus(message, type = 'info') {
    const statusElement = document.getElementById('status');
    statusElement.textContent = message;
    statusElement.className = `status ${type}`;
    statusElement.style.display = 'block';
}
