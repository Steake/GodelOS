/**
 * Error Handling System
 * 
 * Centralized error handling and user feedback for the GödelOS interface
 */

class ErrorHandler {
    constructor() {
        this.errorQueue = [];
        this.errorCounts = new Map();
        this.maxRetries = 3;
        this.retryDelay = 1000;
        
        this.init();
    }

    /**
     * Initialize error handling system
     */
    init() {
        this.setupGlobalErrorHandlers();
        this.setupUserFeedback();
        this.setupErrorReporting();
        
        console.log('✅ Error Handler initialized');
    }

    /**
     * Setup global error handlers
     */
    setupGlobalErrorHandlers() {
        // Handle JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleError({
                type: 'javascript',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error
            });
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError({
                type: 'promise',
                message: event.reason?.message || 'Unhandled promise rejection',
                error: event.reason
            });
        });

        // Handle network errors
        window.addEventListener('online', () => {
            this.handleNetworkRestore();
        });

        window.addEventListener('offline', () => {
            this.handleNetworkError();
        });
    }

    /**
     * Setup user feedback system
     */
    setupUserFeedback() {
        // Create error notification container
        const container = document.createElement('div');
        container.id = 'error-notifications';
        container.className = 'error-notifications';
        document.body.appendChild(container);

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .error-notifications {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
            }
            
            .error-notification {
                background: #ef4444;
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                animation: slideIn 0.3s ease;
            }
            
            .error-notification.warning {
                background: #f59e0b;
            }
            
            .error-notification.info {
                background: #3b82f6;
            }
            
            .error-notification.success {
                background: #10b981;
            }
            
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Setup error reporting
     */
    setupErrorReporting() {
        // Could integrate with error reporting services here
        this.reportingEnabled = false;
    }

    /**
     * Handle error
     */
    handleError(errorInfo) {
        const errorId = this.generateErrorId(errorInfo);
        const count = this.errorCounts.get(errorId) || 0;
        this.errorCounts.set(errorId, count + 1);

        // Avoid spam by limiting duplicate errors
        if (count > 5) {
            return;
        }

        // Add to error queue
        this.errorQueue.push({
            ...errorInfo,
            id: errorId,
            timestamp: Date.now(),
            count: count + 1
        });

        // Process error
        this.processError(errorInfo);

        // Show user notification
        this.showErrorNotification(errorInfo);

        // Log error
        console.error('Error handled:', errorInfo);
    }

    /**
     * Generate error ID for deduplication
     */
    generateErrorId(errorInfo) {
        const key = `${errorInfo.type}-${errorInfo.message}-${errorInfo.filename || ''}`;
        return btoa(key).substring(0, 16);
    }

    /**
     * Process error
     */
    processError(errorInfo) {
        switch (errorInfo.type) {
            case 'network':
                this.handleNetworkError(errorInfo);
                break;
            case 'api':
                this.handleAPIError(errorInfo);
                break;
            case 'validation':
                this.handleValidationError(errorInfo);
                break;
            case 'javascript':
                this.handleJavaScriptError(errorInfo);
                break;
            default:
                this.handleGenericError(errorInfo);
        }
    }

    /**
     * Handle network errors
     */
    handleNetworkError(errorInfo = {}) {
        this.showErrorNotification({
            type: 'network',
            message: 'Network connection lost. Please check your internet connection.',
            level: 'warning'
        });

        // Attempt to reconnect
        this.attemptReconnection();
    }

    /**
     * Handle network restoration
     */
    handleNetworkRestore() {
        this.showErrorNotification({
            type: 'network',
            message: 'Network connection restored.',
            level: 'success'
        });
    }

    /**
     * Handle API errors
     */
    handleAPIError(errorInfo) {
        let message = 'An error occurred while communicating with the server.';
        
        if (errorInfo.status === 404) {
            message = 'The requested resource was not found.';
        } else if (errorInfo.status === 500) {
            message = 'Server error occurred. Please try again later.';
        } else if (errorInfo.status === 403) {
            message = 'Access denied. Please check your permissions.';
        }

        this.showErrorNotification({
            ...errorInfo,
            message,
            level: 'error'
        });
    }

    /**
     * Handle validation errors
     */
    handleValidationError(errorInfo) {
        this.showErrorNotification({
            ...errorInfo,
            level: 'warning'
        });
    }

    /**
     * Handle JavaScript errors
     */
    handleJavaScriptError(errorInfo) {
        // Only show user-friendly message for JS errors
        this.showErrorNotification({
            type: 'javascript',
            message: 'An unexpected error occurred. The page may need to be refreshed.',
            level: 'error'
        });
    }

    /**
     * Handle generic errors
     */
    handleGenericError(errorInfo) {
        this.showErrorNotification({
            ...errorInfo,
            level: 'error'
        });
    }

    /**
     * Show error notification to user
     */
    showErrorNotification(errorInfo) {
        const container = document.getElementById('error-notifications');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `error-notification ${errorInfo.level || 'error'}`;
        notification.textContent = errorInfo.message;

        // Add close button
        const closeButton = document.createElement('button');
        closeButton.textContent = '×';
        closeButton.style.cssText = 'float: right; background: none; border: none; color: inherit; font-size: 18px; cursor: pointer; margin-left: 10px;';
        closeButton.onclick = () => notification.remove();
        notification.appendChild(closeButton);

        container.appendChild(notification);

        // Auto-remove after delay
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, errorInfo.duration || 5000);
    }

    /**
     * Attempt reconnection
     */
    attemptReconnection() {
        // Simple ping to check connectivity
        fetch('/api/health', { method: 'HEAD' })
            .then(() => {
                this.handleNetworkRestore();
            })
            .catch(() => {
                // Retry after delay
                setTimeout(() => {
                    this.attemptReconnection();
                }, 5000);
            });
    }

    /**
     * Retry failed operation
     */
    async retryOperation(operation, maxRetries = this.maxRetries) {
        let lastError;
        
        for (let i = 0; i < maxRetries; i++) {
            try {
                return await operation();
            } catch (error) {
                lastError = error;
                
                if (i < maxRetries - 1) {
                    await this.delay(this.retryDelay * Math.pow(2, i));
                }
            }
        }
        
        throw lastError;
    }

    /**
     * Delay utility
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get error statistics
     */
    getErrorStats() {
        return {
            totalErrors: this.errorQueue.length,
            errorCounts: Object.fromEntries(this.errorCounts),
            recentErrors: this.errorQueue.slice(-10)
        };
    }

    /**
     * Clear error history
     */
    clearErrorHistory() {
        this.errorQueue = [];
        this.errorCounts.clear();
    }

    /**
     * Report error to external service
     */
    reportError(errorInfo) {
        if (!this.reportingEnabled) return;
        
        // Implementation would send to error reporting service
        console.log('Error reported:', errorInfo);
    }
}

// Initialize error handler
const errorHandler = new ErrorHandler();

// Make available globally
window.errorHandler = errorHandler;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorHandler;
}