/**
 * GödelOS Design System
 * 
 * Core design system utilities for managing themes, tokens, and visual consistency
 */

class DesignSystem {
    constructor() {
        this.themes = new Map();
        this.currentTheme = 'dark';
        this.customProperties = new Map();
        this.breakpoints = {
            mobile: 480,
            tablet: 768,
            desktop: 1024,
            wide: 1440
        };
        
        this.init();
    }

    /**
     * Initialize the design system
     */
    init() {
        this.setupThemes();
        this.setupCustomProperties();
        this.setupResponsiveUtilities();
        this.setupColorUtilities();
        this.setupTypographyUtilities();
        
        console.log('✅ Design System initialized');
    }

    /**
     * Setup theme definitions
     */
    setupThemes() {
        // Dark theme (default)
        this.themes.set('dark', {
            name: 'Dark Theme',
            colors: {
                primary: '#6366f1',
                secondary: '#8b5cf6',
                accent: '#06b6d4',
                background: '#0f172a',
                surface: '#1e293b',
                text: '#f8fafc',
                textSecondary: '#cbd5e1',
                textTertiary: '#64748b',
                border: '#334155',
                success: '#10b981',
                warning: '#f59e0b',
                error: '#ef4444',
                info: '#3b82f6'
            },
            gradients: {
                primary: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                secondary: 'linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)',
                surface: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)'
            }
        });

        // Light theme
        this.themes.set('light', {
            name: 'Light Theme',
            colors: {
                primary: '#6366f1',
                secondary: '#8b5cf6',
                accent: '#06b6d4',
                background: '#ffffff',
                surface: '#f8fafc',
                text: '#0f172a',
                textSecondary: '#475569',
                textTertiary: '#64748b',
                border: '#e2e8f0',
                success: '#10b981',
                warning: '#f59e0b',
                error: '#ef4444',
                info: '#3b82f6'
            },
            gradients: {
                primary: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                secondary: 'linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)',
                surface: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
            }
        });

        // High contrast theme
        this.themes.set('high-contrast', {
            name: 'High Contrast Theme',
            colors: {
                primary: '#ffffff',
                secondary: '#ffff00',
                accent: '#00ffff',
                background: '#000000',
                surface: '#1a1a1a',
                text: '#ffffff',
                textSecondary: '#ffffff',
                textTertiary: '#cccccc',
                border: '#ffffff',
                success: '#00ff00',
                warning: '#ffff00',
                error: '#ff0000',
                info: '#00ffff'
            },
            gradients: {
                primary: 'linear-gradient(135deg, #ffffff 0%, #cccccc 100%)',
                secondary: 'linear-gradient(135deg, #ffff00 0%, #00ffff 100%)',
                surface: 'linear-gradient(135deg, #1a1a1a 0%, #333333 100%)'
            }
        });
    }

    /**
     * Setup CSS custom properties
     */
    setupCustomProperties() {
        const root = document.documentElement;
        const theme = this.themes.get(this.currentTheme);
        
        if (theme) {
            // Set color properties
            Object.entries(theme.colors).forEach(([key, value]) => {
                root.style.setProperty(`--color-${key}`, value);
            });
            
            // Set gradient properties
            Object.entries(theme.gradients).forEach(([key, value]) => {
                root.style.setProperty(`--gradient-${key}`, value);
            });
        }
        
        // Set spacing scale
        const spacingScale = {
            0: '0',
            1: '0.25rem',
            2: '0.5rem',
            3: '0.75rem',
            4: '1rem',
            5: '1.25rem',
            6: '1.5rem',
            8: '2rem',
            10: '2.5rem',
            12: '3rem',
            16: '4rem',
            20: '5rem',
            24: '6rem'
        };
        
        Object.entries(spacingScale).forEach(([key, value]) => {
            root.style.setProperty(`--spacing-${key}`, value);
        });
        
        // Set typography scale
        const typographyScale = {
            xs: '0.75rem',
            sm: '0.875rem',
            base: '1rem',
            lg: '1.125rem',
            xl: '1.25rem',
            '2xl': '1.5rem',
            '3xl': '1.875rem',
            '4xl': '2.25rem',
            '5xl': '3rem',
            '6xl': '3.75rem'
        };
        
        Object.entries(typographyScale).forEach(([key, value]) => {
            root.style.setProperty(`--text-${key}`, value);
        });
        
        // Set border radius scale
        const borderRadiusScale = {
            none: '0',
            sm: '0.125rem',
            base: '0.25rem',
            md: '0.375rem',
            lg: '0.5rem',
            xl: '0.75rem',
            '2xl': '1rem',
            '3xl': '1.5rem',
            full: '9999px'
        };
        
        Object.entries(borderRadiusScale).forEach(([key, value]) => {
            root.style.setProperty(`--radius-${key}`, value);
        });
        
        // Set shadow scale
        const shadowScale = {
            sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
            base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
            md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
            lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
            xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
            '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
            inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)'
        };
        
        Object.entries(shadowScale).forEach(([key, value]) => {
            root.style.setProperty(`--shadow-${key}`, value);
        });
    }

    /**
     * Setup responsive utilities
     */
    setupResponsiveUtilities() {
        // Add viewport meta tag if not present
        if (!document.querySelector('meta[name="viewport"]')) {
            const viewport = document.createElement('meta');
            viewport.name = 'viewport';
            viewport.content = 'width=device-width, initial-scale=1.0';
            document.head.appendChild(viewport);
        }
        
        // Setup responsive classes
        this.setupResponsiveClasses();
    }

    /**
     * Setup responsive classes
     */
    setupResponsiveClasses() {
        const style = document.createElement('style');
        style.textContent = `
            /* Responsive utilities */
            .mobile-only { display: none; }
            .tablet-only { display: none; }
            .desktop-only { display: none; }
            .wide-only { display: none; }
            
            @media (max-width: ${this.breakpoints.mobile}px) {
                .mobile-only { display: block; }
                .mobile-hidden { display: none; }
            }
            
            @media (min-width: ${this.breakpoints.mobile + 1}px) and (max-width: ${this.breakpoints.tablet}px) {
                .tablet-only { display: block; }
                .tablet-hidden { display: none; }
            }
            
            @media (min-width: ${this.breakpoints.tablet + 1}px) and (max-width: ${this.breakpoints.desktop}px) {
                .desktop-only { display: block; }
                .desktop-hidden { display: none; }
            }
            
            @media (min-width: ${this.breakpoints.wide}px) {
                .wide-only { display: block; }
                .wide-hidden { display: none; }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Setup color utilities
     */
    setupColorUtilities() {
        // Color utility functions are available via CSS custom properties
        // Additional JavaScript utilities can be added here
    }

    /**
     * Setup typography utilities
     */
    setupTypographyUtilities() {
        // Typography utility functions
        const style = document.createElement('style');
        style.textContent = `
            /* Typography utilities */
            .text-xs { font-size: var(--text-xs); }
            .text-sm { font-size: var(--text-sm); }
            .text-base { font-size: var(--text-base); }
            .text-lg { font-size: var(--text-lg); }
            .text-xl { font-size: var(--text-xl); }
            .text-2xl { font-size: var(--text-2xl); }
            .text-3xl { font-size: var(--text-3xl); }
            .text-4xl { font-size: var(--text-4xl); }
            .text-5xl { font-size: var(--text-5xl); }
            .text-6xl { font-size: var(--text-6xl); }
            
            .font-thin { font-weight: 100; }
            .font-light { font-weight: 300; }
            .font-normal { font-weight: 400; }
            .font-medium { font-weight: 500; }
            .font-semibold { font-weight: 600; }
            .font-bold { font-weight: 700; }
            .font-extrabold { font-weight: 800; }
            .font-black { font-weight: 900; }
            
            .leading-tight { line-height: 1.25; }
            .leading-snug { line-height: 1.375; }
            .leading-normal { line-height: 1.5; }
            .leading-relaxed { line-height: 1.625; }
            .leading-loose { line-height: 2; }
        `;
        document.head.appendChild(style);
    }

    /**
     * Switch theme
     */
    setTheme(themeName) {
        if (this.themes.has(themeName)) {
            this.currentTheme = themeName;
            this.setupCustomProperties();
            
            // Update body class
            document.body.className = document.body.className.replace(/theme-\w+/g, '');
            document.body.classList.add(`theme-${themeName}`);
            
            // Dispatch theme change event
            document.dispatchEvent(new CustomEvent('themeChanged', {
                detail: { theme: themeName }
            }));
            
            console.log(`🎨 Theme switched to: ${themeName}`);
        } else {
            console.warn(`Theme "${themeName}" not found`);
        }
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Get available themes
     */
    getAvailableThemes() {
        return Array.from(this.themes.keys());
    }

    /**
     * Add custom theme
     */
    addTheme(name, theme) {
        this.themes.set(name, theme);
        console.log(`🎨 Custom theme "${name}" added`);
    }

    /**
     * Get breakpoint value
     */
    getBreakpoint(name) {
        return this.breakpoints[name];
    }

    /**
     * Check if current viewport matches breakpoint
     */
    matchesBreakpoint(breakpoint) {
        const width = window.innerWidth;
        
        switch (breakpoint) {
            case 'mobile':
                return width <= this.breakpoints.mobile;
            case 'tablet':
                return width > this.breakpoints.mobile && width <= this.breakpoints.tablet;
            case 'desktop':
                return width > this.breakpoints.tablet && width <= this.breakpoints.desktop;
            case 'wide':
                return width > this.breakpoints.desktop;
            default:
                return false;
        }
    }

    /**
     * Get current breakpoint
     */
    getCurrentBreakpoint() {
        const width = window.innerWidth;
        
        if (width <= this.breakpoints.mobile) return 'mobile';
        if (width <= this.breakpoints.tablet) return 'tablet';
        if (width <= this.breakpoints.desktop) return 'desktop';
        return 'wide';
    }

    /**
     * Generate color variations
     */
    generateColorVariations(baseColor, steps = 9) {
        // This would typically use a color manipulation library
        // For now, return the base color
        return Array(steps).fill(baseColor);
    }

    /**
     * Calculate contrast ratio
     */
    calculateContrastRatio(color1, color2) {
        // Simplified contrast calculation
        // In a real implementation, this would calculate proper WCAG contrast ratios
        return 4.5; // Placeholder value
    }

    /**
     * Check if color combination meets accessibility standards
     */
    meetsAccessibilityStandards(foreground, background, level = 'AA') {
        const contrast = this.calculateContrastRatio(foreground, background);
        
        switch (level) {
            case 'AA':
                return contrast >= 4.5;
            case 'AAA':
                return contrast >= 7;
            default:
                return contrast >= 3;
        }
    }

    /**
     * Apply motion preferences
     */
    applyMotionPreferences() {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        if (prefersReducedMotion) {
            document.documentElement.style.setProperty('--animation-duration', '0.01ms');
            document.documentElement.style.setProperty('--transition-duration', '0.01ms');
        } else {
            document.documentElement.style.setProperty('--animation-duration', '200ms');
            document.documentElement.style.setProperty('--transition-duration', '150ms');
        }
        
        return prefersReducedMotion;
    }

    /**
     * Apply color scheme preferences
     */
    applyColorSchemePreferences() {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (prefersDark && this.currentTheme === 'light') {
            this.setTheme('dark');
        } else if (!prefersDark && this.currentTheme === 'dark') {
            this.setTheme('light');
        }
        
        return prefersDark;
    }

    /**
     * Setup system preference listeners
     */
    setupSystemPreferenceListeners() {
        // Listen for color scheme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            this.applyColorSchemePreferences();
        });
        
        // Listen for motion preference changes
        window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', () => {
            this.applyMotionPreferences();
        });
        
        // Listen for contrast preference changes
        window.matchMedia('(prefers-contrast: high)').addEventListener('change', (e) => {
            if (e.matches) {
                this.setTheme('high-contrast');
            } else {
                this.applyColorSchemePreferences();
            }
        });
    }

    /**
     * Initialize system preferences
     */
    initializeSystemPreferences() {
        this.applyMotionPreferences();
        this.applyColorSchemePreferences();
        this.setupSystemPreferenceListeners();
        
        // Check for high contrast preference
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            this.setTheme('high-contrast');
        }
    }
}

// Initialize design system
const designSystem = new DesignSystem();

// Apply system preferences
designSystem.initializeSystemPreferences();

// Make available globally
window.designSystem = designSystem;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DesignSystem;
}