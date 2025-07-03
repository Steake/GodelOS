/**
 * GödelOS Adaptive Interface System
 * 
 * Implements the three-tier complexity system with progressive disclosure
 * and accessibility features as specified in the UI/UX design document
 */

class AdaptiveInterface {
    constructor() {
        this.complexityLevel = 'intermediate'; // Default level
        this.complexityThresholds = {
            novice: 0,
            intermediate: 1,
            expert: 2
        };
        this.disclosureSections = new Map();
        this.userPreferences = this.loadUserPreferences();
        this.accessibilityFeatures = {
            reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
            highContrast: window.matchMedia('(forced-colors: active)').matches,
            screenReader: this.detectScreenReader()
        };
        
        this.init();
    }

    /**
     * Initialize the adaptive interface system
     */
    init() {
        this.setupComplexityControls();
        this.setupProgressiveDisclosure();
        this.setupOnboarding();
        this.setupAccessibilityFeatures();
        this.setupUserPreferences();
        this.setupKeyboardNavigation();
        this.setupTooltips();
        
        // Apply initial complexity level
        this.setComplexityLevel(this.userPreferences.complexityLevel || 'intermediate');
        
        // Listen for media query changes
        this.setupMediaQueryListeners();
        
        console.log('🎯 Adaptive Interface System initialized');
    }

    /**
     * Setup complexity level controls
     */
    setupComplexityControls() {
        const complexityRadios = document.querySelectorAll('input[name="complexity"]');
        
        complexityRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.setComplexityLevel(e.target.value);
                    this.announceToScreenReader(`Complexity level changed to ${e.target.value}`);
                }
            });
        });

        // Legacy select support
        const complexitySelect = document.getElementById('complexitySelect');
        if (complexitySelect) {
            complexitySelect.addEventListener('change', (e) => {
                this.setComplexityLevel(e.target.value);
            });
        }
    }

    /**
     * Set the complexity level and update interface
     */
    setComplexityLevel(level) {
        // Prevent recursion by checking if this is already the current level
        if (this.complexityLevel === level) {
            return;
        }
        
        const previousLevel = this.complexityLevel;
        this.complexityLevel = level;
        
        // Update body attribute
        document.body.setAttribute('data-complexity', level);
        
        // Update radio buttons
        const radio = document.getElementById(level);
        if (radio) {
            radio.checked = true;
        }
        
        // Update legacy select
        const select = document.getElementById('complexitySelect');
        if (select) {
            select.value = level;
        }
        
        // Apply progressive disclosure
        this.applyProgressiveDisclosure();
        
        // Update onboarding if active
        this.updateOnboardingForComplexity();
        
        // Save preference
        this.saveUserPreference('complexityLevel', level);
        
        // Trigger custom event
        this.dispatchEvent('complexityChanged', {
            previousLevel,
            currentLevel: level,
            threshold: this.complexityThresholds[level]
        });
        
        console.log(`🎯 Complexity level set to: ${level}`);
    }

    /**
     * Apply progressive disclosure based on complexity level
     */
    applyProgressiveDisclosure() {
        const currentThreshold = this.complexityThresholds[this.complexityLevel];
        
        // Show/hide elements based on complexity thresholds
        document.querySelectorAll('[data-complexity-threshold]').forEach(element => {
            const elementThreshold = parseInt(element.getAttribute('data-complexity-threshold'));
            
            if (elementThreshold <= currentThreshold) {
                this.showElement(element);
            } else {
                this.hideElement(element);
            }
        });
        
        // Update disclosure sections
        this.disclosureSections.forEach((section, id) => {
            this.updateDisclosureSection(id);
        });
    }

    /**
     * Setup progressive disclosure sections
     */
    setupProgressiveDisclosure() {
        const disclosureTriggers = document.querySelectorAll('.disclosure-trigger');
        
        disclosureTriggers.forEach(trigger => {
            const section = trigger.closest('.disclosure-section');
            if (!section) return; // Skip if no section found
            
            const content = section.querySelector('.disclosure-content');
            if (!content) return; // Skip if no content found
            
            const sectionId = section.id || `disclosure-${Date.now()}-${Math.random()}`;
            
            if (!section.id) {
                section.id = sectionId;
            }
            
            // Store section data
            this.disclosureSections.set(sectionId, {
                trigger,
                content,
                section,
                expanded: trigger.getAttribute('aria-expanded') === 'true',
                threshold: parseInt(section.getAttribute('data-complexity-threshold') || '0')
            });
            
            // Setup trigger event
            trigger.addEventListener('click', () => {
                this.toggleDisclosure(sectionId);
            });
            
            // Setup keyboard support
            trigger.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleDisclosure(sectionId);
                }
            });
            
            // Initial state
            this.updateDisclosureSection(sectionId);
        });
    }

    /**
     * Toggle disclosure section
     */
    toggleDisclosure(sectionId) {
        const section = this.disclosureSections.get(sectionId);
        if (!section) return;
        
        const wasExpanded = section.expanded;
        section.expanded = !wasExpanded;
        
        // Update ARIA attributes
        section.trigger.setAttribute('aria-expanded', section.expanded);
        
        // Update content classes
        if (section.expanded) {
            section.content.classList.remove('collapsed');
            section.content.classList.add('expanded');
        } else {
            section.content.classList.remove('expanded');
            section.content.classList.add('collapsed');
        }
        
        // Update action text
        const actionElement = section.trigger.querySelector('.disclosure-action');
        if (actionElement) {
            actionElement.textContent = section.expanded ? 'Hide' : 'Show';
        }
        
        // Announce to screen readers
        const titleElement = section.trigger.querySelector('.disclosure-title');
        const title = titleElement ? titleElement.textContent : 'Section';
        this.announceToScreenReader(`${title} ${section.expanded ? 'expanded' : 'collapsed'}`);
        
        // Save state
        this.saveUserPreference(`disclosure-${sectionId}`, section.expanded);
    }

    /**
     * Update disclosure section based on complexity
     */
    updateDisclosureSection(sectionId) {
        const section = this.disclosureSections.get(sectionId);
        if (!section) return;
        
        const currentThreshold = this.complexityThresholds[this.complexityLevel];
        const shouldShow = section.threshold <= currentThreshold;
        
        if (shouldShow) {
            this.showElement(section.section);
            
            // Restore saved state
            const savedState = this.getUserPreference(`disclosure-${sectionId}`);
            if (savedState !== null) {
                section.expanded = savedState;
                section.trigger.setAttribute('aria-expanded', section.expanded);
                
                if (section.expanded) {
                    section.content.classList.remove('collapsed');
                    section.content.classList.add('expanded');
                } else {
                    section.content.classList.remove('expanded');
                    section.content.classList.add('collapsed');
                }
            }
        } else {
            this.hideElement(section.section);
        }
    }

    /**
     * Setup onboarding system
     */
    setupOnboarding() {
        this.onboarding = {
            currentStep: 1,
            totalSteps: 4,
            isActive: !this.getUserPreference('onboardingCompleted'),
            selectedComplexity: 'intermediate'
        };
        
        if (!this.onboarding.isActive) {
            this.hideOnboarding();
            return;
        }
        
        this.setupOnboardingControls();
        this.showOnboarding();
    }

    /**
     * Setup onboarding controls
     */
    setupOnboardingControls() {
        const nextBtn = document.getElementById('onboardingNext');
        const prevBtn = document.getElementById('onboardingPrev');
        const skipBtn = document.getElementById('onboardingSkip');
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextOnboardingStep());
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prevOnboardingStep());
        }
        
        if (skipBtn) {
            skipBtn.addEventListener('click', () => this.skipOnboarding());
        }
        
        // Setup step dots
        document.querySelectorAll('.step-dot').forEach((dot, index) => {
            dot.addEventListener('click', () => {
                this.goToOnboardingStep(index + 1);
            });
        });
        
        // Setup complexity selection in onboarding
        document.querySelectorAll('.complexity-option').forEach(option => {
            option.addEventListener('click', () => {
                document.querySelectorAll('.complexity-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                option.classList.add('selected');
                this.onboarding.selectedComplexity = option.getAttribute('data-level');
            });
        });
        
        // Setup example query buttons
        document.querySelectorAll('.example-query').forEach(button => {
            button.addEventListener('click', () => {
                const query = button.getAttribute('data-query');
                this.finishOnboarding(query);
            });
        });
    }

    /**
     * Show onboarding overlay
     */
    showOnboarding() {
        const overlay = document.getElementById('onboardingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
            overlay.setAttribute('aria-hidden', 'false');
            
            // Focus management
            const firstStep = overlay.querySelector('.onboarding-step.active');
            if (firstStep) {
                firstStep.focus();
            }
            
            // Prevent body scroll
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * Hide onboarding overlay
     */
    hideOnboarding() {
        const overlay = document.getElementById('onboardingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
            overlay.setAttribute('aria-hidden', 'true');
            
            // Restore body scroll
            document.body.style.overflow = '';
            
            // Focus main content
            const mainContent = document.getElementById('main-content');
            if (mainContent) {
                mainContent.focus();
            }
        }
    }

    /**
     * Navigate to next onboarding step
     */
    nextOnboardingStep() {
        if (this.onboarding.currentStep < this.onboarding.totalSteps) {
            this.goToOnboardingStep(this.onboarding.currentStep + 1);
        } else {
            this.finishOnboarding();
        }
    }

    /**
     * Navigate to previous onboarding step
     */
    prevOnboardingStep() {
        if (this.onboarding.currentStep > 1) {
            this.goToOnboardingStep(this.onboarding.currentStep - 1);
        }
    }

    /**
     * Go to specific onboarding step
     */
    goToOnboardingStep(step) {
        // Hide current step
        const currentStep = document.querySelector(`.onboarding-step[data-step="${this.onboarding.currentStep}"]`);
        if (currentStep) {
            currentStep.classList.remove('active');
        }
        
        // Show new step
        const newStep = document.querySelector(`.onboarding-step[data-step="${step}"]`);
        if (newStep) {
            newStep.classList.add('active');
        }
        
        // Update step indicators
        document.querySelectorAll('.step-dot').forEach((dot, index) => {
            if (index + 1 === step) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
        
        // Update navigation buttons
        const prevBtn = document.getElementById('onboardingPrev');
        const nextBtn = document.getElementById('onboardingNext');
        
        if (prevBtn) {
            prevBtn.style.display = step === 1 ? 'none' : 'block';
        }
        
        if (nextBtn) {
            nextBtn.textContent = step === this.onboarding.totalSteps ? 'Get Started' : 'Next';
        }
        
        this.onboarding.currentStep = step;
        
        // Announce step change
        this.announceToScreenReader(`Step ${step} of ${this.onboarding.totalSteps}`);
    }

    /**
     * Skip onboarding
     */
    skipOnboarding() {
        this.finishOnboarding();
    }

    /**
     * Finish onboarding
     */
    finishOnboarding(initialQuery = null) {
        // Apply selected complexity
        this.setComplexityLevel(this.onboarding.selectedComplexity);
        
        // Mark as completed
        this.saveUserPreference('onboardingCompleted', true);
        
        // Hide overlay
        this.hideOnboarding();
        
        // If initial query provided, populate it
        if (initialQuery) {
            const queryInput = document.getElementById('naturalLanguageQuery');
            if (queryInput) {
                queryInput.value = initialQuery;
                queryInput.focus();
            }
        }
        
        // Trigger completion event
        this.dispatchEvent('onboardingCompleted', {
            selectedComplexity: this.onboarding.selectedComplexity,
            initialQuery
        });
        
        console.log('🎓 Onboarding completed');
    }

    /**
     * Update onboarding for current complexity level
     */
    updateOnboardingForComplexity() {
        // This could update onboarding content based on complexity
        // For now, it's a placeholder for future enhancements
    }

    /**
     * Setup accessibility features
     */
    setupAccessibilityFeatures() {
        // Reduced motion support
        if (this.accessibilityFeatures.reducedMotion) {
            document.body.setAttribute('data-reduced-motion', 'true');
        }
        
        // High contrast support
        if (this.accessibilityFeatures.highContrast) {
            document.body.setAttribute('data-high-contrast', 'true');
        }
        
        // Screen reader announcements
        this.setupScreenReaderAnnouncements();
        
        // Focus management
        this.setupFocusManagement();
        
        // ARIA live regions
        this.setupLiveRegions();
    }

    /**
     * Setup screen reader announcements
     */
    setupScreenReaderAnnouncements() {
        this.announcementRegion = document.getElementById('announcements');
        if (!this.announcementRegion) {
            this.announcementRegion = document.createElement('div');
            this.announcementRegion.id = 'announcements';
            this.announcementRegion.setAttribute('aria-live', 'polite');
            this.announcementRegion.setAttribute('aria-atomic', 'true');
            this.announcementRegion.className = 'sr-only';
            document.body.appendChild(this.announcementRegion);
        }
    }

    /**
     * Announce message to screen readers
     */
    announceToScreenReader(message) {
        if (this.announcementRegion) {
            this.announcementRegion.textContent = message;
            
            // Clear after announcement
            setTimeout(() => {
                this.announcementRegion.textContent = '';
            }, 1000);
        }
    }

    /**
     * Setup focus management
     */
    setupFocusManagement() {
        // Track focus for better keyboard navigation
        let lastFocusedElement = null;
        
        document.addEventListener('focusin', (e) => {
            lastFocusedElement = e.target;
        });
        
        // Store reference for modal focus management
        this.lastFocusedElement = lastFocusedElement;
    }

    /**
     * Setup live regions for dynamic content
     */
    setupLiveRegions() {
        // Status updates
        const statusElements = document.querySelectorAll('[id$="Status"]');
        statusElements.forEach(element => {
            if (!element.hasAttribute('aria-live')) {
                element.setAttribute('aria-live', 'polite');
            }
        });
        
        // Loading indicators
        const loadingElements = document.querySelectorAll('.loading-indicator');
        loadingElements.forEach(element => {
            if (!element.hasAttribute('aria-live')) {
                element.setAttribute('aria-live', 'polite');
            }
        });
    }

    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl+Enter to submit query
            if (e.ctrlKey && e.key === 'Enter') {
                const queryForm = document.getElementById('queryForm');
                if (queryForm) {
                    queryForm.dispatchEvent(new Event('submit'));
                }
            }
            
            // Escape to close modals
            if (e.key === 'Escape') {
                this.closeActiveModals();
            }
            
            // Alt+1,2,3 for complexity levels
            if (e.altKey && ['1', '2', '3'].includes(e.key)) {
                const levels = ['novice', 'intermediate', 'expert'];
                const level = levels[parseInt(e.key) - 1];
                this.setComplexityLevel(level);
            }
        });
    }

    /**
     * Setup tooltips
     */
    setupTooltips() {
        // Enhanced tooltip support for touch devices
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            // Touch support
            element.addEventListener('touchstart', (e) => {
                this.showTooltip(element);
            });
            
            // Hide on touch outside
            document.addEventListener('touchstart', (e) => {
                if (!element.contains(e.target)) {
                    this.hideTooltip(element);
                }
            });
        });
    }

    /**
     * Show tooltip
     */
    showTooltip(element) {
        // Implementation for enhanced tooltips
        // This is a placeholder for future tooltip enhancements
    }

    /**
     * Hide tooltip
     */
    hideTooltip(element) {
        // Implementation for enhanced tooltips
        // This is a placeholder for future tooltip enhancements
    }

    /**
     * Close active modals
     */
    closeActiveModals() {
        // Close onboarding
        if (this.onboarding.isActive) {
            this.skipOnboarding();
        }
        
        // Close other modals (help, examples, etc.)
        const modals = document.querySelectorAll('.modal-overlay');
        modals.forEach(modal => {
            if (modal.style.display !== 'none') {
                modal.style.display = 'none';
            }
        });
    }

    /**
     * Setup media query listeners
     */
    setupMediaQueryListeners() {
        // Reduced motion
        const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        reducedMotionQuery.addListener((e) => {
            this.accessibilityFeatures.reducedMotion = e.matches;
            document.body.setAttribute('data-reduced-motion', e.matches);
        });
        
        // High contrast
        const highContrastQuery = window.matchMedia('(forced-colors: active)');
        highContrastQuery.addListener((e) => {
            this.accessibilityFeatures.highContrast = e.matches;
            document.body.setAttribute('data-high-contrast', e.matches);
        });
    }

    /**
     * Detect screen reader
     */
    detectScreenReader() {
        // Simple screen reader detection
        return navigator.userAgent.includes('NVDA') || 
               navigator.userAgent.includes('JAWS') || 
               window.speechSynthesis !== undefined;
    }

    /**
     * Show element with animation
     */
    showElement(element) {
        element.style.display = '';
        element.setAttribute('aria-hidden', 'false');
        
        if (!this.accessibilityFeatures.reducedMotion) {
            element.classList.add('animate-fade-in');
        }
    }

    /**
     * Hide element
     */
    hideElement(element) {
        element.style.display = 'none';
        element.setAttribute('aria-hidden', 'true');
    }

    /**
     * Setup user preferences
     */
    setupUserPreferences() {
        // Load saved preferences
        const saved = this.loadUserPreferences();
        
        // Apply saved complexity level
        if (saved.complexityLevel) {
            this.setComplexityLevel(saved.complexityLevel);
        }
        
        // Apply other preferences
        Object.keys(saved).forEach(key => {
            if (key.startsWith('disclosure-')) {
                const sectionId = key.replace('disclosure-', '');
                const section = this.disclosureSections.get(sectionId);
                if (section) {
                    section.expanded = saved[key];
                }
            }
        });
    }

    /**
     * Load user preferences from localStorage
     */
    loadUserPreferences() {
        try {
            const saved = localStorage.getItem('godelos-preferences');
            return saved ? JSON.parse(saved) : {};
        } catch (error) {
            console.warn('Failed to load user preferences:', error);
            return {};
        }
    }

    /**
     * Save user preference
     */
    saveUserPreference(key, value) {
        try {
            const preferences = this.loadUserPreferences();
            preferences[key] = value;
            localStorage.setItem('godelos-preferences', JSON.stringify(preferences));
        } catch (error) {
            console.warn('Failed to save user preference:', error);
        }
    }

    /**
     * Get user preference
     */
    getUserPreference(key) {
        const preferences = this.loadUserPreferences();
        return preferences[key];
    }

    /**
     * Dispatch custom event
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: {
                ...detail,
                timestamp: Date.now(),
                complexityLevel: this.complexityLevel
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Get current complexity level
     */
    getComplexityLevel() {
        return this.complexityLevel;
    }

    /**
     * Get complexity threshold
     */
    getComplexityThreshold() {
        return this.complexityThresholds[this.complexityLevel];
    }

    /**
     * Check if feature should be visible
     */
    isFeatureVisible(threshold) {
        return threshold <= this.getComplexityThreshold();
    }

    /**
     * Restart onboarding
     */
    restartOnboarding() {
        this.saveUserPreference('onboardingCompleted', false);
        this.onboarding.isActive = true;
        this.onboarding.currentStep = 1;
        this.setupOnboarding();
    }
}

// Initialize adaptive interface when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.adaptiveInterface = new AdaptiveInterface();
    });
} else {
    window.adaptiveInterface = new AdaptiveInterface();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdaptiveInterface;
}