/**
 * Accessibility Enhancement System
 * 
 * Provides comprehensive accessibility features for the GödelOS interface
 */

class AccessibilityEnhancer {
    constructor() {
        this.settings = {
            highContrast: false,
            reducedMotion: false,
            largeText: false,
            screenReaderMode: false
        };
        
        this.init();
    }

    /**
     * Initialize accessibility system
     */
    init() {
        this.setupScreenReaderSupport();
        this.setupKeyboardNavigation();
        this.setupFocusManagement();
        this.setupAccessibilityControls();
        this.detectUserPreferences();
        
        console.log('✅ Accessibility Enhancer initialized');
    }

    /**
     * Setup screen reader support
     */
    setupScreenReaderSupport() {
        // Create announcement region
        const announcer = document.createElement('div');
        announcer.id = 'screen-reader-announcements';
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';
        document.body.appendChild(announcer);

        // Add screen reader styles
        const style = document.createElement('style');
        style.textContent = `
            .sr-only {
                position: absolute !important;
                width: 1px !important;
                height: 1px !important;
                padding: 0 !important;
                margin: -1px !important;
                overflow: hidden !important;
                clip: rect(0, 0, 0, 0) !important;
                white-space: nowrap !important;
                border: 0 !important;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Modal escape handling
            if (e.key === 'Escape') {
                this.handleEscapeKey();
            }

            // Accessibility shortcuts
            if (e.altKey && e.key === 'c') {
                e.preventDefault();
                this.toggleHighContrast();
            }
        });
    }

    /**
     * Handle escape key press
     */
    handleEscapeKey() {
        const openModals = document.querySelectorAll('.modal-overlay:not([style*="display: none"])');
        if (openModals.length > 0) {
            const topModal = openModals[openModals.length - 1];
            const closeButton = topModal.querySelector('.modal-close, [data-dismiss="modal"]');
            if (closeButton) {
                closeButton.click();
            }
        }
    }

    /**
     * Setup focus management
     */
    setupFocusManagement() {
        // Add focus styles
        const style = document.createElement('style');
        style.textContent = `
            .focus-visible,
            *:focus-visible {
                outline: 2px solid var(--color-primary, #6366f1) !important;
                outline-offset: 2px !important;
                border-radius: 4px;
            }
            
            .high-contrast .focus-visible,
            .high-contrast *:focus-visible {
                outline: 3px solid #ffff00 !important;
                outline-offset: 2px !important;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Setup accessibility controls
     */
    setupAccessibilityControls() {
        // Add high contrast styles
        const style = document.createElement('style');
        style.id = 'high-contrast-styles';
        style.disabled = true;
        style.textContent = `
            .high-contrast {
                filter: contrast(150%) brightness(110%);
            }
            
            .high-contrast * {
                background-color: #000000 !important;
                color: #ffffff !important;
                border-color: #ffffff !important;
            }
            
            .high-contrast .btn-primary {
                background-color: #ffffff !important;
                color: #000000 !important;
                border: 2px solid #ffffff !important;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Detect user preferences from system
     */
    detectUserPreferences() {
        // High contrast preference
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            this.toggleHighContrast(true);
        }
        
        // Reduced motion preference
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.toggleReducedMotion(true);
        }
    }

    /**
     * Toggle high contrast mode
     */
    toggleHighContrast(enabled = !this.settings.highContrast) {
        this.settings.highContrast = enabled;
        const style = document.getElementById('high-contrast-styles');
        
        if (enabled) {
            document.body.classList.add('high-contrast');
            if (style) style.disabled = false;
            this.announceToScreenReader('High contrast mode enabled');
        } else {
            document.body.classList.remove('high-contrast');
            if (style) style.disabled = true;
            this.announceToScreenReader('High contrast mode disabled');
        }
    }

    /**
     * Toggle reduced motion mode
     */
    toggleReducedMotion(enabled = !this.settings.reducedMotion) {
        this.settings.reducedMotion = enabled;
        
        if (enabled) {
            const style = document.createElement('style');
            style.id = 'reduced-motion-styles';
            style.textContent = `
                *,
                *::before,
                *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                    scroll-behavior: auto !important;
                }
            `;
            document.head.appendChild(style);
        } else {
            const existingStyle = document.getElementById('reduced-motion-styles');
            if (existingStyle) {
                existingStyle.remove();
            }
        }
        
        const message = enabled ? 'Reduced motion mode enabled' : 'Reduced motion mode disabled';
        this.announceToScreenReader(message);
    }

    /**
     * Announce message to screen readers
     */
    announceToScreenReader(message) {
        const announcer = document.getElementById('screen-reader-announcements');
        if (announcer) {
            announcer.textContent = message;
            
            // Clear after announcement
            setTimeout(() => {
                announcer.textContent = '';
            }, 1000);
        }
    }

    /**
     * Get current accessibility settings
     */
    getSettings() {
        return { ...this.settings };
    }

    /**
     * Apply accessibility settings
     */
    applySettings(settings) {
        Object.keys(settings).forEach(key => {
            if (key in this.settings) {
                this.settings[key] = settings[key];
                
                switch (key) {
                    case 'highContrast':
                        this.toggleHighContrast(settings[key]);
                        break;
                    case 'reducedMotion':
                        this.toggleReducedMotion(settings[key]);
                        break;
                }
            }
        });
    }
}

// Initialize accessibility enhancer
const accessibilityEnhancer = new AccessibilityEnhancer();

// Make available globally
window.accessibilityEnhancer = accessibilityEnhancer;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AccessibilityEnhancer;
}