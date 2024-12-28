let mediaRecorder;
let audioChunks = [];
let audioStream;

// More reliable media support check
async function checkMediaSupport() {
    try {
        // Modern browsers
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            return navigator.mediaDevices;
        }
        
        // Legacy browsers
        const getUserMedia = 
            navigator.getUserMedia ||
            navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia ||
            navigator.msGetUserMedia;

        if (!getUserMedia) {
            throw new Error('Media capture not supported. Please use Chrome, Firefox, or Edge.');
        }

        // Create a mediaDevices shim for older browsers
        navigator.mediaDevices = {
            getUserMedia: function(constraints) {
                return new Promise((resolve, reject) => {
                    getUserMedia.call(navigator, constraints, resolve, reject);
                });
            }
        };
        
        return navigator.mediaDevices;
    } catch (e) {
        throw new Error(`Media initialization failed: ${e.message}`);
    }
}

async function requestMicrophoneAccess() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop()); // Stop the test stream
        showStatus('Microphone access granted!', 'success');
        document.getElementById('permissionRequest').style.display = 'none';
        document.getElementById('startBtn').disabled = false;
        return true;
    } catch (error) {
        showStatus('Could not access microphone. Please check browser settings.', 'error');
        console.error('Microphone access error:', error);
        return false;
    }
}

// Replace checkSecureContext with simpler permission check
async function checkMicrophonePermission() {
    try {
        // Check if permission is already granted
        const result = await navigator.permissions.query({ name: 'microphone' });
        
        if (result.state === 'granted') {
            document.getElementById('permissionRequest').style.display = 'none';
            return true;
        }
        
        // Show permission request if not granted
        document.getElementById('permissionRequest').style.display = 'block';
        document.getElementById('startBtn').disabled = true;
        return false;
        
    } catch (e) {
        // Fallback for browsers that don't support permissions API
        return requestMicrophoneAccess();
    }
}

async function checkSecureContext() {
    // In development, accept self-signed certificates
    const isDevelopment = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1' ||
                         window.location.hostname === '172.22.191.182';
    
    if (isDevelopment) {
        console.log("[DEBUG] Development environment detected, accepting self-signed certificate");
        return true;
    }
    
    if (!window.isSecureContext) {
        throw new Error('HTTPS connection required for microphone access');
    }
    return true;
}

function updateUI(isRecording) {
    document.getElementById('startBtn').disabled = isRecording;
    document.getElementById('stopBtn').disabled = !isRecording;
    document.getElementById('recordingStatus').style.display = isRecording ? 'inline' : 'none';
}

function showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('status');
    statusDiv.innerHTML = `<span class="${type}">${message}</span>`;
}

// Update window.onload
window.onload = async function() {
    // Check microphone permission on page load
    await checkMicrophonePermission();
    
    if (typeof MediaRecorder === 'undefined') {
        showError('Your browser does not support MediaRecorder. Please use Chrome, Firefox, or Edge.');
        document.getElementById('startBtn').disabled = true;
    }
};

// Update startRecording
async function startRecording() {
    try {
        // Request permission if not already granted
        if (!await requestMicrophoneAccess()) {
            throw new Error('Microphone access required');
        }

        const mediaDevices = await checkMediaSupport();
        audioChunks = [];
        
        console.log("[DEBUG] Requesting microphone access...");
        audioStream = await mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 44100
            },
            video: false
        });
        
        console.log("[DEBUG] Microphone access granted");
        
        // Create MediaRecorder with fallback
        try {
            mediaRecorder = new MediaRecorder(audioStream, {
                mimeType: 'audio/webm;codecs=opus'
            });
        } catch (e) {
            console.warn("Preferred codec not supported, using default");
            mediaRecorder = new MediaRecorder(audioStream);
        }

        mediaRecorder.addEventListener("dataavailable", event => {
            audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener("stop", async () => {
            try {
                document.getElementById('loadingStatus').style.display = 'block';
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const formData = new FormData();
                formData.append('audio', audioBlob, 'audio.webm');

                console.log("[DEBUG] Preparing to send audio...");
                const response = await fetch('/api/upload', {  // Updated to use /api prefix
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                console.log("[DEBUG] Response status:", response.status);
                console.log("[DEBUG] Response headers:", response.headers);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                if (data.transcription) {
                    document.getElementById('transcription').textContent = data.transcription;
                    showStatus('Transcription complete!', 'success');
                } else {
                    throw new Error(data.error || 'No transcription received');
                }
            } catch (error) {
                console.error("[ERROR] Upload failed:", error);
                showStatus(`Error: ${error.message}`, 'error');
                console.error('Upload error:', error);
            } finally {
                document.getElementById('loadingStatus').style.display = 'none';
            }
        });

        mediaRecorder.start();
        updateUI(true);
        showStatus('Recording in progress...', 'success');
    } catch (error) {
        console.error("[ERROR] Media initialization failed:", error);
        showStatus(`Microphone access error: ${error.message}. Please ensure microphone permissions are granted.`, 'error');
        updateUI(false);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        if (audioStream) {
            audioStream.getTracks().forEach(track => track.stop());
        }
        updateUI(false);
    }
}
