/**
 * Progressive Disclosure System
 * 
 * Manages the progressive disclosure of interface complexity based on user expertise
 */

class ProgressiveDisclosure {
    constructor() {
        this.complexityLevels = {
            novice: 0,
            intermediate: 1,
            expert: 2
        };
        
        this.currentLevel = 1; // Default to intermediate
        this.disclosureRules = new Map();
        this.animationDuration = 200;
        
        this.init();
    }

    /**
     * Initialize progressive disclosure system
     */
    init() {
        this.setupDisclosureRules();
        this.setupObservers();
        this.bindEvents();
        
        console.log('✅ Progressive Disclosure initialized');
    }

    /**
     * Setup disclosure rules for different complexity levels
     */
    setupDisclosureRules() {
        // Define what elements should be shown at each complexity level
        this.disclosureRules.set('novice', {
            show: [
                '.complexity-novice',
                '.basic-controls',
                '.simple-visualizations',
                '.guided-tutorials'
            ],
            hide: [
                '.complexity-intermediate',
                '.complexity-expert',
                '.advanced-controls',
                '.technical-details',
                '.expert-visualizations'
            ]
        });

        this.disclosureRules.set('intermediate', {
            show: [
                '.complexity-novice',
                '.complexity-intermediate',
                '.basic-controls',
                '.intermediate-controls',
                '.standard-visualizations'
            ],
            hide: [
                '.complexity-expert',
                '.expert-controls',
                '.technical-details',
                '.expert-visualizations'
            ]
        });

        this.disclosureRules.set('expert', {
            show: [
                '.complexity-novice',
                '.complexity-intermediate',
                '.complexity-expert',
                '.basic-controls',
                '.intermediate-controls',
                '.expert-controls',
                '.technical-details',
                '.expert-visualizations'
            ],
            hide: []
        });
    }

    /**
     * Setup mutation observers to handle dynamically added content
     */
    setupObservers() {
        this.observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.processElement(node);
                        }
                    });
                }
            });
        });

        this.observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    /**
     * Bind events for complexity changes
     */
    bindEvents() {
        document.addEventListener('complexityChanged', (event) => {
            this.setComplexityLevel(event.detail.currentLevel);
        });

        // Handle data-complexity-threshold attributes
        document.addEventListener('DOMContentLoaded', () => {
            this.applyCurrentLevel();
        });
    }

    /**
     * Set complexity level and update interface
     */
    setComplexityLevel(level) {
        const levelName = typeof level === 'string' ? level : this.getLevelName(level);
        const levelNumber = typeof level === 'number' ? level : this.complexityLevels[level];
        
        this.currentLevel = levelNumber;
        this.applyDisclosureRules(levelName);
        this.updateThresholdElements();
        
        console.log(`🎯 Progressive disclosure updated to: ${levelName}`);
    }

    /**
     * Get level name from number
     */
    getLevelName(levelNumber) {
        const entries = Object.entries(this.complexityLevels);
        const found = entries.find(([, value]) => value === levelNumber);
        return found ? found[0] : 'intermediate';
    }

    /**
     * Apply disclosure rules for the given level
     */
    applyDisclosureRules(levelName) {
        const rules = this.disclosureRules.get(levelName);
        if (!rules) return;

        // Show elements
        rules.show.forEach(selector => {
            this.showElements(selector);
        });

        // Hide elements
        rules.hide.forEach(selector => {
            this.hideElements(selector);
        });
    }

    /**
     * Update elements with data-complexity-threshold attributes
     */
    updateThresholdElements() {
        const elements = document.querySelectorAll('[data-complexity-threshold]');
        
        elements.forEach(element => {
            const threshold = parseInt(element.getAttribute('data-complexity-threshold'));
            
            if (this.currentLevel >= threshold) {
                this.showElement(element);
            } else {
                this.hideElement(element);
            }
        });
    }

    /**
     * Show elements matching selector
     */
    showElements(selector) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => this.showElement(element));
    }

    /**
     * Hide elements matching selector
     */
    hideElements(selector) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => this.hideElement(element));
    }

    /**
     * Show individual element with animation
     */
    showElement(element) {
        if (element.classList.contains('disclosure-hidden')) {
            element.classList.remove('disclosure-hidden');
            element.style.display = '';
            
            // Animate in
            element.style.opacity = '0';
            element.style.transform = 'translateY(-10px)';
            
            requestAnimationFrame(() => {
                element.style.transition = `opacity ${this.animationDuration}ms ease, transform ${this.animationDuration}ms ease`;
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
                
                setTimeout(() => {
                    element.style.transition = '';
                }, this.animationDuration);
            });
        }
    }

    /**
     * Hide individual element with animation
     */
    hideElement(element) {
        if (!element.classList.contains('disclosure-hidden')) {
            element.style.transition = `opacity ${this.animationDuration}ms ease, transform ${this.animationDuration}ms ease`;
            element.style.opacity = '0';
            element.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                element.classList.add('disclosure-hidden');
                element.style.display = 'none';
                element.style.transition = '';
            }, this.animationDuration);
        }
    }

    /**
     * Process newly added element
     */
    processElement(element) {
        // Check if element has complexity classes
        const hasComplexityClass = Array.from(element.classList).some(cls => 
            cls.startsWith('complexity-')
        );
        
        if (hasComplexityClass) {
            this.applyCurrentLevel();
        }

        // Check for threshold attributes
        if (element.hasAttribute('data-complexity-threshold')) {
            const threshold = parseInt(element.getAttribute('data-complexity-threshold'));
            
            if (this.currentLevel >= threshold) {
                this.showElement(element);
            } else {
                this.hideElement(element);
            }
        }

        // Process child elements
        const childrenWithThresholds = element.querySelectorAll('[data-complexity-threshold]');
        childrenWithThresholds.forEach(child => {
            const threshold = parseInt(child.getAttribute('data-complexity-threshold'));
            
            if (this.currentLevel >= threshold) {
                this.showElement(child);
            } else {
                this.hideElement(child);
            }
        });
    }

    /**
     * Apply current complexity level
     */
    applyCurrentLevel() {
        const levelName = this.getLevelName(this.currentLevel);
        this.applyDisclosureRules(levelName);
        this.updateThresholdElements();
    }

    /**
     * Get current complexity level
     */
    getCurrentLevel() {
        return this.currentLevel;
    }

    /**
     * Get current level name
     */
    getCurrentLevelName() {
        return this.getLevelName(this.currentLevel);
    }

    /**
     * Add custom disclosure rule
     */
    addDisclosureRule(levelName, rule) {
        const existingRule = this.disclosureRules.get(levelName) || { show: [], hide: [] };
        
        if (rule.show) {
            existingRule.show = [...existingRule.show, ...rule.show];
        }
        
        if (rule.hide) {
            existingRule.hide = [...existingRule.hide, ...rule.hide];
        }
        
        this.disclosureRules.set(levelName, existingRule);
    }

    /**
     * Remove disclosure rule
     */
    removeDisclosureRule(levelName, selector) {
        const rule = this.disclosureRules.get(levelName);
        if (rule) {
            rule.show = rule.show.filter(s => s !== selector);
            rule.hide = rule.hide.filter(s => s !== selector);
        }
    }

    /**
     * Toggle element visibility based on complexity
     */
    toggleElementComplexity(element, minLevel) {
        const threshold = typeof minLevel === 'string' ? this.complexityLevels[minLevel] : minLevel;
        element.setAttribute('data-complexity-threshold', threshold);
        
        if (this.currentLevel >= threshold) {
            this.showElement(element);
        } else {
            this.hideElement(element);
        }
    }

    /**
     * Create progressive disclosure container
     */
    createDisclosureContainer(config) {
        const container = document.createElement('div');
        container.className = 'disclosure-container';
        
        // Add content for each level
        Object.entries(config).forEach(([level, content]) => {
            const levelElement = document.createElement('div');
            levelElement.className = `complexity-${level}`;
            levelElement.innerHTML = content;
            container.appendChild(levelElement);
        });
        
        return container;
    }

    /**
     * Destroy progressive disclosure system
     */
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        
        document.removeEventListener('complexityChanged', this.handleComplexityChange);
        
        // Show all hidden elements
        const hiddenElements = document.querySelectorAll('.disclosure-hidden');
        hiddenElements.forEach(element => {
            element.classList.remove('disclosure-hidden');
            element.style.display = '';
        });
        
        console.log('🗑️ Progressive Disclosure destroyed');
    }
}

// Initialize progressive disclosure
const progressiveDisclosure = new ProgressiveDisclosure();

// Make available globally
window.progressiveDisclosure = progressiveDisclosure;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProgressiveDisclosure;
}