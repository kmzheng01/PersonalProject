// AudioStream Web Application Frontend

class AudioStreamApp {
    constructor() {
        this.apiBase = '/api';
        this.currentTrack = null;
        this.playlist = [];
        this.isPlaying = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDeviceInfo();
        this.updateOutputs();
    }

    setupEventListeners() {
        // Playback controls
        document.getElementById('playBtn').addEventListener('click', () => this.play());
        document.getElementById('pauseBtn').addEventListener('click', () => this.pause());
        document.getElementById('stopBtn').addEventListener('click', () => this.stop());
        document.getElementById('nextBtn').addEventListener('click', () => this.next());
        document.getElementById('previousBtn').addEventListener('click', () => this.previous());

        // Volume
        document.getElementById('volumeSlider').addEventListener('input', (e) => {
            this.setVolume(e.target.value / 100);
        });

        // Progress bar
        document.getElementById('progressBar').addEventListener('change', (e) => {
            this.seek(e.target.value);
        });

        // File upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.backgroundColor = 'rgba(29, 185, 84, 0.3)';
        });
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.backgroundColor = '';
        });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.backgroundColor = '';
            this.handleFileUpload(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });

        // Library
        document.getElementById('scanBtn').addEventListener('click', () => this.scanLibrary());
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.searchLibrary(e.target.value);
        });

        // Output selection
        document.getElementById('outputSelect').addEventListener('change', (e) => {
            this.selectOutput(e.target.value);
        });
    }

    async apiCall(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.apiBase}${endpoint}`, options);
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            return { error: error.message };
        }
    }

    async play() {
        await this.apiCall('/player/play', 'POST');
        this.isPlaying = true;
        this.updatePlaybackUI();
    }

    async pause() {
        await this.apiCall('/player/pause', 'POST');
        this.isPlaying = false;
        this.updatePlaybackUI();
    }

    async stop() {
        await this.apiCall('/player/stop', 'POST');
        this.isPlaying = false;
        this.updatePlaybackUI();
    }

    async next() {
        await this.apiCall('/player/next', 'POST');
    }

    async previous() {
        await this.apiCall('/player/previous', 'POST');
    }

    async seek(position) {
        await this.apiCall('/player/seek', 'POST', { position });
    }

    async setVolume(volume) {
        await this.apiCall('/player/volume', 'POST', { volume });
        document.getElementById('volumeValue').textContent = Math.round(volume * 100) + '%';
    }

    async selectOutput(outputId) {
        await this.apiCall(`/outputs/${outputId}`, 'POST');
    }

    async updatePlaybackUI() {
        const status = await this.apiCall('/player/status');
        document.getElementById('trackTitle').textContent = status.file || 'No Track';
        document.getElementById('currentTime').textContent = this.formatTime(status.position || 0);
        document.getElementById('duration').textContent = this.formatTime(status.duration || 0);
        document.getElementById('progressBar').value = (status.position / status.duration) * 100 || 0;
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    async handleFileUpload(files) {
        const statusDiv = document.getElementById('uploadStatus');
        statusDiv.innerHTML = '';

        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);

            const statusItem = document.createElement('div');
            statusItem.className = 'upload-item';
            statusItem.innerHTML = `<span>${file.name}</span><span>Uploading...</span>`;
            statusDiv.appendChild(statusItem);

            try {
                const response = await fetch(`${this.apiBase}/upload`, {
                    method: 'POST',
                    body: formData,
                });

                const result = await response.json();

                if (result.success) {
                    statusItem.innerHTML = `<span>${file.name}</span><span style="color: #1db954;">✓ Uploaded</span>`;
                } else {
                    statusItem.innerHTML = `<span>${file.name}</span><span style="color: #ff4444;">✗ Failed</span>`;
                }
            } catch (error) {
                statusItem.innerHTML = `<span>${file.name}</span><span style="color: #ff4444;">✗ Error</span>`;
            }
        }
    }

    async scanLibrary() {
        await this.apiCall('/library/scan', 'POST', { directory: './music' });
        this.loadLibrary();
    }

    async loadLibrary() {
        const result = await this.apiCall('/library/list?limit=100');
        const libraryList = document.getElementById('libraryList');
        libraryList.innerHTML = '';

        if (!result.tracks || result.tracks.length === 0) {
            libraryList.innerHTML = '<p>No tracks in library</p>';
            return;
        }

        result.tracks.forEach(track => {
            const item = document.createElement('div');
            item.className = 'track-item';
            item.innerHTML = `
                <strong>${track.title}</strong>
                <p>${track.artist} - ${track.album}</p>
            `;
            item.addEventListener('click', () => this.playTrack(track));
            libraryList.appendChild(item);
        });
    }

    async searchLibrary(query) {
        if (!query) {
            this.loadLibrary();
            return;
        }

        const result = await this.apiCall(`/library/search?q=${encodeURIComponent(query)}`);
        // Update UI with search results
    }

    async playTrack(track) {
        await this.apiCall('/player/load', 'POST', { filepath: track.filepath });
        this.play();
    }

    async updateOutputs() {
        const result = await this.apiCall('/outputs');
        const select = document.getElementById('outputSelect');
        select.innerHTML = '';

        if (result.outputs) {
            result.outputs.forEach(output => {
                const option = document.createElement('option');
                option.value = output.id;
                option.textContent = output.name;
                select.appendChild(option);
            });
        }
    }

    async loadDeviceInfo() {
        const result = await this.apiCall('/device/info');
        document.getElementById('version').textContent = result.version || '1.0.0';
        document.getElementById('platform').textContent = result.platform || 'Unknown';

        // Update uptime periodically
        setInterval(() => {
            const uptime = Math.floor((result.uptime || 0) / 60);
            const hours = Math.floor(uptime / 60);
            const mins = uptime % 60;
            document.getElementById('uptime').textContent = `${hours}h ${mins}m`;
        }, 5000);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AudioStreamApp();
});
