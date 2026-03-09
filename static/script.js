// QR Code Functionality
document.addEventListener('DOMContentLoaded', function() {
    const qrTypeSelect = document.getElementById('qr-type');
    const previewBtn = document.getElementById('preview-btn');
    const generateBtn = document.getElementById('generate-btn');
    const downloadBtn = document.getElementById('download-btn');
    const qrPreview = document.getElementById('qr-preview');

    if (qrTypeSelect) {
        qrTypeSelect.addEventListener('change', updateFormFields);
        updateFormFields();
    }

    if (previewBtn) {
        previewBtn.addEventListener('click', generateQRCode);
    }

    if (generateBtn) {
        generateBtn.addEventListener('click', () => generateQRCode(true));
    }

    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', switchTab);
    });
});

function updateFormFields() {
    const type = document.getElementById('qr-type')?.value;
    const fieldsContainer = document.getElementById('qr-fields');
    
    if (!fieldsContainer) return;

    let html = '';

    switch(type) {
        case 'url':
            html = `
                <div class="form-group">
                    <label for="url">Website URL</label>
                    <input type="text" id="url" name="url" placeholder="https://example.com" required>
                </div>
            `;
            break;
        case 'text':
            html = `
                <div class="form-group">
                    <label for="text">Text Content</label>
                    <textarea id="text" name="text" placeholder="Enter your text here..." required></textarea>
                </div>
            `;
            break;
        case 'wifi':
            html = `
                <div class="form-group">
                    <label for="ssid">Network Name (SSID)</label>
                    <input type="text" id="ssid" name="ssid" placeholder="WiFi Network Name" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="WiFi Password" required>
                </div>
                <div class="form-group">
                    <label for="encryption">Encryption Type</label>
                    <select id="encryption" name="encryption">
                        <option value="WPA">WPA/WPA2</option>
                        <option value="WEP">WEP</option>
                        <option value="nopass">No Password</option>
                    </select>
                </div>
            `;
            break;
        case 'phone':
            html = `
                <div class="form-group">
                    <label for="phone">Phone Number</label>
                    <input type="tel" id="phone" name="phone" placeholder="+1-555-000-0000" required>
                </div>
            `;
            break;
        case 'sms':
            html = `
                <div class="form-group">
                    <label for="phone">Phone Number</label>
                    <input type="tel" id="phone" name="phone" placeholder="+1-555-000-0000" required>
                </div>
                <div class="form-group">
                    <label for="message">Message (Optional)</label>
                    <textarea id="message" name="message" placeholder="SMS message content"></textarea>
                </div>
            `;
            break;
        case 'email':
            html = `
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" placeholder="example@email.com" required>
                </div>
                <div class="form-group">
                    <label for="subject">Subject (Optional)</label>
                    <input type="text" id="subject" name="subject" placeholder="Email subject">
                </div>
                <div class="form-group">
                    <label for="body">Message (Optional)</label>
                    <textarea id="body" name="body" placeholder="Email message"></textarea>
                </div>
            `;
            break;
        case 'contact':
            html = `
                <div class="form-group">
                    <label for="name">Full Name</label>
                    <input type="text" id="name" name="name" placeholder="John Doe" required>
                </div>
                <div class="form-group">
                    <label for="contact-phone">Phone Number</label>
                    <input type="tel" id="contact-phone" name="phone" placeholder="+1-555-000-0000">
                </div>
                <div class="form-group">
                    <label for="contact-email">Email Address</label>
                    <input type="email" id="contact-email" name="email" placeholder="john@example.com">
                </div>
                <div class="form-group">
                    <label for="company">Company (Optional)</label>
                    <input type="text" id="company" name="company" placeholder="Company Name">
                </div>
            `;
            break;
        case 'location':
            html = `
                <div class="form-group">
                    <label for="address">Address or Location</label>
                    <input type="text" id="address" name="address" placeholder="e.g., Times Square, New York" required>
                </div>
            `;
            break;
        case 'event':
            html = `
                <div class="form-group">
                    <label for="event-title">Event Title</label>
                    <input type="text" id="event-title" name="event_title" placeholder="Conference 2024" required>
                </div>
                <div class="form-group">
                    <label for="start-date">Start Date & Time</label>
                    <input type="datetime-local" id="start-date" name="start_date" required>
                </div>
                <div class="form-group">
                    <label for="event-location">Event Location</label>
                    <input type="text" id="event-location" name="event_location" placeholder="Meeting Room A">
                </div>
            `;
            break;
        default:
            html = `<p>Select a QR type to get started</p>`;
    }

    fieldsContainer.innerHTML = html;
}

function generateQRCode(download = false) {
    const type = document.getElementById('qr-type')?.value;
    const format = document.getElementById('format')?.value || 'png';
    const fgColor = document.getElementById('fg-color')?.value || '#000000';
    const bgColor = document.getElementById('bg-color')?.value || '#FFFFFF';
    const logo = document.getElementById('logo')?.files[0];
    const title = document.getElementById('title')?.value || `QR-${new Date().toLocaleString()}`;

    if (!type) {
        showAlert('Please select a QR code type', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('type', type);
    formData.append('format', format);
    formData.append('fg_color', fgColor);
    formData.append('bg_color', bgColor);
    formData.append('title', title);

    // Add type-specific data
    switch(type) {
        case 'url':
            formData.append('url', document.getElementById('url')?.value || '');
            break;
        case 'text':
            formData.append('text', document.getElementById('text')?.value || '');
            break;
        case 'wifi':
        case 'wifi2':
            formData.append('ssid', document.getElementById('ssid')?.value || '');
            formData.append('password', document.getElementById('password')?.value || '');
            formData.append('encryption', document.getElementById('encryption')?.value || 'WPA');
            if (type === 'wifi2') {
                formData.append('hidden', document.getElementById('hidden')?.checked || false);
            }
            break;
        case 'phone':
        case 'sms':
            formData.append('phone', document.getElementById('phone')?.value || '');
            if (type === 'sms') {
                formData.append('message', document.getElementById('message')?.value || '');
            }
            break;
        case 'email':
            formData.append('email', document.getElementById('email')?.value || '');
            formData.append('subject', document.getElementById('subject')?.value || '');
            formData.append('body', document.getElementById('body')?.value || '');
            break;
        case 'contact':
            formData.append('name', document.getElementById('name')?.value || '');
            formData.append('phone', document.getElementById('contact-phone')?.value || '');
            formData.append('email', document.getElementById('contact-email')?.value || '');
            break;
        case 'location':
            formData.append('address', document.getElementById('address')?.value || '');
            break;
        case 'event':
            formData.append('event_title', document.getElementById('event-title')?.value || '');
            formData.append('start_date', document.getElementById('start-date')?.value || '');
            formData.append('event_location', document.getElementById('event-location')?.value || '');
            break;
    }

    if (logo) {
        formData.append('logo', logo);
    }

    const endpoint = download ? '/generate' : '/preview';
    const loadingElement = document.getElementById('qr-loading');

    if (loadingElement) {
        loadingElement.style.display = 'flex';
    }

    fetch(endpoint, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to generate QR code');
        if (download) return response.blob();
        return response.json();
    })
    .then(data => {
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }

        if (download) {
            // Handle file download
            const url = window.URL.createObjectURL(new Blob([data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${title}.${format}`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(url);
            showAlert('QR code downloaded successfully!', 'success');
        } else {
            // Display preview
            if (data.image) {
                const qrPreview = document.getElementById('qr-preview');
                if (qrPreview) {
                    qrPreview.innerHTML = `<img src="${data.image}" alt="QR Code" style="max-width: 300px;">`;
                    document.getElementById('download-btn').style.display = 'block';
                }
            }
        }
    })
    .catch(error => {
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        showAlert(error.message || 'Error generating QR code', 'error');
        console.error('Error:', error);
    });
}

function switchTab(e) {
    const tabName = e.target.getAttribute('data-tab');
    
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to clicked tab and its content
    e.target.classList.add('active');
    document.getElementById(tabName)?.classList.add('active');
}

function showAlert(message, type = 'success') {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;

    alertsContainer.appendChild(alert);

    setTimeout(() => {
        alert.style.animation = 'fadeUp 0.3s ease-out';
        setTimeout(() => alert.remove(), 300);
    }, 3000);
}

// Analytics track
function trackEvent(eventName, data = {}) {
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, data);
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Color Picker Integration
document.addEventListener('DOMContentLoaded', function() {
    const fgColorInput = document.getElementById('fg-color');
    const bgColorInput = document.getElementById('bg-color');

    if (fgColorInput) {
        fgColorInput.addEventListener('input', function() {
            document.body.style.setProperty('--preview-fg', this.value);
        });
    }

    if (bgColorInput) {
        bgColorInput.addEventListener('input', function() {
            document.body.style.setProperty('--preview-bg', this.value);
        });
    }
});

// Mobile Menu Toggle
function toggleMobileMenu() {
    const nav = document.querySelector('nav');
    if (nav) {
        nav.classList.toggle('active');
    }
}
