/**
 * College ERP Notification Manager
 * Handles Firebase Cloud Messaging notifications with proper permission management
 */

class NotificationManager {
    constructor(firebaseConfig, tokenEndpoint) {
        this.firebaseConfig = firebaseConfig;
        this.tokenEndpoint = tokenEndpoint;
        this.messaging = null;
        this.isInitialized = false;
        
        this.init();
    }

    init() {
        if (!this.isSupported()) {
            console.warn('Notifications are not supported in this browser.');
            return;
        }

        try {
            // Initialize Firebase
            firebase.initializeApp(this.firebaseConfig);
            this.messaging = firebase.messaging();
            this.isInitialized = true;
            
            this.setupMessageHandlers();
            this.checkPermissionStatus();
        } catch (error) {
            console.error('Failed to initialize Firebase:', error);
        }
    }

    isSupported() {
        return 'Notification' in window && 'serviceWorker' in navigator && firebase;
    }

    checkPermissionStatus() {
        if (!this.isInitialized) return;

        switch (Notification.permission) {
            case 'granted':
                console.log('Notification permission already granted.');
                this.getAndSendToken();
                break;
            case 'denied':
                console.log('Notification permission has been blocked.');
                this.showPermissionBlockedMessage();
                break;
            case 'default':
                // Don't request immediately on page load
                console.log('Notification permission not requested yet.');
                this.showPermissionPrompt();
                break;
        }
    }

    async requestPermission() {
        if (!this.isInitialized) return false;

        try {
            const permission = await this.messaging.requestPermission();
            console.log('Notification permission granted.');
            this.getAndSendToken();
            this.hidePermissionPrompt();
            return true;
        } catch (error) {
            console.log('Unable to get permission to notify.', error);
            return false;
        }
    }

    getAndSendToken() {
        if (!this.isInitialized) return;

        this.messaging.getToken().then(token => {
            if (token) {
                console.log('FCM Token:', token);
                this.sendTokenToServer(token);
            } else {
                console.log('No registration token available.');
            }
        }).catch(err => {
            console.log('An error occurred while retrieving token:', err);
        });
    }

    sendTokenToServer(token) {
        $.ajax({
            url: this.tokenEndpoint,
            type: 'POST',
            data: {
                token: token,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: (response) => {
                console.log('Token sent to server successfully');
            },
            error: (response) => {
                console.log('Failed to send token to server');
            }
        });
    }

    setupMessageHandlers() {
        if (!this.isInitialized) return;

        // Handle incoming messages when app is in foreground
        this.messaging.onMessage(payload => {
            console.log('Message received:', payload);
            
            if (Notification.permission === 'granted') {
                this.showNotification(payload);
            }
        });

        // Handle token refresh
        this.messaging.onTokenRefresh(() => {
            this.messaging.getToken().then(newToken => {
                console.log('New Token:', newToken);
                this.sendTokenToServer(newToken);
            }).catch(err => {
                console.log('Unable to retrieve refreshed token:', err);
            });
        });
    }

    showNotification(payload) {
        const notificationOptions = {
            body: payload.notification.body,
            icon: payload.notification.icon || '/static/dist/img/virus.png',
            badge: '/static/dist/img/virus.png',
            tag: 'college-erp-notification',
            requireInteraction: true,
            data: payload.data
        };

        const notification = new Notification(payload.notification.title, notificationOptions);
        
        notification.onclick = (event) => {
            event.preventDefault();
            window.focus();
            
            if (payload.notification.click_action) {
                window.open(payload.notification.click_action, '_blank');
            }
            
            notification.close();
        };

        // Auto-close after 5 seconds
        setTimeout(() => {
            notification.close();
        }, 5000);
    }

    showPermissionPrompt() {
        // Create a subtle notification prompt
        const promptHtml = `
            <div id="notification-prompt" class="alert alert-info alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; max-width: 350px;">
                <div class="d-flex align-items-center">
                    <i class="fas fa-bell me-2"></i>
                    <div class="flex-grow-1">
                        <strong>Stay Updated!</strong><br>
                        <small>Enable notifications to receive important updates.</small>
                    </div>
                </div>
                <div class="mt-2">
                    <button type="button" class="btn btn-primary btn-sm me-2" onclick="notificationManager.requestPermission()">
                        Enable
                    </button>
                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="notificationManager.hidePermissionPrompt()">
                        Maybe Later
                    </button>
                </div>
            </div>
        `;
        
        // Only show if not already shown
        if (!document.getElementById('notification-prompt')) {
            document.body.insertAdjacentHTML('beforeend', promptHtml);
            
            // Auto-hide after 10 seconds
            setTimeout(() => {
                this.hidePermissionPrompt();
            }, 10000);
        }
    }

    showPermissionBlockedMessage() {
        const blockedHtml = `
            <div id="notification-blocked" class="alert alert-warning alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; max-width: 350px;">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <div>
                    <strong>Notifications Blocked</strong><br>
                    <small>To receive updates, please enable notifications in your browser settings.</small>
                </div>
                <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
            </div>
        `;
        
        if (!document.getElementById('notification-blocked')) {
            document.body.insertAdjacentHTML('beforeend', blockedHtml);
            
            // Auto-hide after 8 seconds
            setTimeout(() => {
                const element = document.getElementById('notification-blocked');
                if (element) element.remove();
            }, 8000);
        }
    }

    hidePermissionPrompt() {
        const prompt = document.getElementById('notification-prompt');
        if (prompt) {
            prompt.remove();
        }
    }

    // Public method to manually request permission (for button clicks, etc.)
    enableNotifications() {
        this.requestPermission();
    }

    // Check if notifications are enabled
    isEnabled() {
        return Notification.permission === 'granted';
    }

    // Get current permission status
    getPermissionStatus() {
        return Notification.permission;
    }
}

// Global instance will be created by each page with their specific config
window.NotificationManager = NotificationManager;
