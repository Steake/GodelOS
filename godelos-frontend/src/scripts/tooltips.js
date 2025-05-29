/**
 * Tooltip System
 */

class TooltipManager {
    constructor() {
        this.tooltip = null;
        this.init();
    }

    init() {
        this.createTooltip();
        this.setupEventListeners();
        console.log('✅ Tooltip Manager initialized');
    }

    createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'tooltip';
        this.tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 14px;
            pointer-events: none;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.2s;
        `;
        document.body.appendChild(this.tooltip);
    }

    setupEventListeners() {
        document.addEventListener('mouseover', (e) => {
            const tooltip = e.target.getAttribute('data-tooltip') || e.target.getAttribute('title');
            if (tooltip) {
                this.showTooltip(e, tooltip);
                e.target.removeAttribute('title'); // Prevent default tooltip
            }
        });

        document.addEventListener('mousemove', (e) => {
            if (this.tooltip.style.opacity === '1') {
                this.updateTooltipPosition(e);
            }
        });

        document.addEventListener('mouseout', (e) => {
            if (e.target.hasAttribute('data-tooltip') || e.target.hasAttribute('title')) {
                this.hideTooltip();
            }
        });
    }

    showTooltip(event, text) {
        this.tooltip.textContent = text;
        this.updateTooltipPosition(event);
        this.tooltip.style.opacity = '1';
    }

    hideTooltip() {
        this.tooltip.style.opacity = '0';
    }

    updateTooltipPosition(event) {
        const x = event.clientX + 10;
        const y = event.clientY - 30;
        
        this.tooltip.style.left = x + 'px';
        this.tooltip.style.top = y + 'px';
    }
}

// Initialize tooltip manager
const tooltipManager = new TooltipManager();

// Make available globally
window.tooltipManager = tooltipManager;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TooltipManager;
}