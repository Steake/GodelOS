/**
 * Modal Management System
 * 
 * Simple modal management for the GödelOS interface
 */

class ModalManager {
    constructor() {
        this.activeModals = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        console.log('✅ Modal Manager initialized');
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal(e.target);
            }
            
            if (e.target.classList.contains('modal-close')) {
                const modal = e.target.closest('.modal-overlay');
                if (modal) this.closeModal(modal);
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModals.length > 0) {
                this.closeTopModal();
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            modal.setAttribute('aria-hidden', 'false');
            this.activeModals.push(modal);
            
            const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            
            const index = this.activeModals.indexOf(modal);
            if (index > -1) {
                this.activeModals.splice(index, 1);
            }
        }
    }

    closeTopModal() {
        if (this.activeModals.length > 0) {
            const topModal = this.activeModals[this.activeModals.length - 1];
            this.closeModal(topModal);
        }
    }

    closeAllModals() {
        [...this.activeModals].forEach(modal => this.closeModal(modal));
    }
}

// Initialize modal manager
const modalManager = new ModalManager();

// Make available globally
window.modalManager = modalManager;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModalManager;
}