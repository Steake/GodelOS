/**
 * Performance Optimization System
 * 
 * Monitors and optimizes performance for the GödelOS interface
 */

class PerformanceOptimizer {
    constructor() {
        this.metrics = {};
        this.observers = {};
        this.thresholds = {
            loadTime: 3000,
            firstPaint: 1000,
            largestContentfulPaint: 2500,
            cumulativeLayoutShift: 0.1
        };
        
        this.init();
    }

    /**
     * Initialize performance monitoring
     */
    init() {
        this.setupPerformanceObservers();
        this.setupResourceOptimization();
        this.setupMemoryMonitoring();
        this.startMetricsCollection();
        
        console.log('✅ Performance Optimizer initialized');
    }

    /**
     * Setup performance observers
     */
    setupPerformanceObservers() {
        // Observe paint timing
        if ('PerformanceObserver' in window) {
            try {
                const paintObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        this.metrics[entry.name] = entry.startTime;
                    }
                });
                paintObserver.observe({ entryTypes: ['paint'] });
                this.observers.paint = paintObserver;
            } catch (e) {
                console.warn('Paint observer not supported');
            }

            // Observe largest contentful paint
            try {
                const lcpObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    this.metrics.largestContentfulPaint = lastEntry.startTime;
                });
                lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
                this.observers.lcp = lcpObserver;
            } catch (e) {
                console.warn('LCP observer not supported');
            }

            // Observe layout shifts
            try {
                const clsObserver = new PerformanceObserver((list) => {
                    let clsValue = 0;
                    for (const entry of list.getEntries()) {
                        if (!entry.hadRecentInput) {
                            clsValue += entry.value;
                        }
                    }
                    this.metrics.cumulativeLayoutShift = clsValue;
                });
                clsObserver.observe({ entryTypes: ['layout-shift'] });
                this.observers.cls = clsObserver;
            } catch (e) {
                console.warn('CLS observer not supported');
            }
        }
    }

    /**
     * Setup resource optimization
     */
    setupResourceOptimization() {
        // Lazy load images
        this.setupLazyLoading();
        
        // Optimize animations based on device capabilities
        this.optimizeAnimations();
        
        // Debounce resize events
        this.setupDebouncedEvents();
    }

    /**
     * Setup lazy loading for images
     */
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                            imageObserver.unobserve(img);
                        }
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });

            this.observers.images = imageObserver;
        }
    }

    /**
     * Optimize animations based on device capabilities
     */
    optimizeAnimations() {
        // Reduce animations on low-end devices
        const isLowEndDevice = navigator.hardwareConcurrency <= 2 || 
                              navigator.deviceMemory <= 2;
        
        if (isLowEndDevice) {
            document.documentElement.style.setProperty('--animation-duration', '0.1s');
            document.documentElement.style.setProperty('--transition-duration', '0.1s');
        }
    }

    /**
     * Setup debounced events
     */
    setupDebouncedEvents() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });
    }

    /**
     * Handle resize events
     */
    handleResize() {
        // Optimize layout for new viewport size
        this.optimizeForViewport();
    }

    /**
     * Optimize for current viewport
     */
    optimizeForViewport() {
        const width = window.innerWidth;
        
        // Disable complex animations on small screens
        if (width < 768) {
            document.body.classList.add('mobile-optimized');
        } else {
            document.body.classList.remove('mobile-optimized');
        }
    }

    /**
     * Setup memory monitoring
     */
    setupMemoryMonitoring() {
        if ('memory' in performance) {
            setInterval(() => {
                this.collectMemoryMetrics();
            }, 30000); // Every 30 seconds
        }
    }

    /**
     * Collect memory metrics
     */
    collectMemoryMetrics() {
        if ('memory' in performance) {
            this.metrics.memory = {
                used: performance.memory.usedJSHeapSize,
                total: performance.memory.totalJSHeapSize,
                limit: performance.memory.jsHeapSizeLimit
            };
            
            // Warn if memory usage is high
            const usagePercent = (this.metrics.memory.used / this.metrics.memory.limit) * 100;
            if (usagePercent > 80) {
                console.warn('High memory usage detected:', usagePercent.toFixed(2) + '%');
                this.optimizeMemoryUsage();
            }
        }
    }

    /**
     * Optimize memory usage
     */
    optimizeMemoryUsage() {
        // Clear unused cached data
        if (window.caches) {
            // Could implement cache cleanup here
        }
        
        // Suggest garbage collection
        if (window.gc) {
            window.gc();
        }
    }

    /**
     * Start metrics collection
     */
    startMetricsCollection() {
        // Collect initial metrics
        setTimeout(() => {
            this.collectInitialMetrics();
        }, 1000);
        
        // Collect periodic metrics
        setInterval(() => {
            this.collectPeriodicMetrics();
        }, 60000); // Every minute
    }

    /**
     * Collect initial performance metrics
     */
    collectInitialMetrics() {
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
            this.metrics.loadTime = navigation.loadEventEnd - navigation.loadEventStart;
            this.metrics.domContentLoaded = navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart;
            this.metrics.timeToInteractive = navigation.loadEventEnd;
        }
    }

    /**
     * Collect periodic metrics
     */
    collectPeriodicMetrics() {
        // Update current metrics
        this.collectMemoryMetrics();
        
        // Log performance summary
        console.log('📊 Performance metrics:', this.getMetricsSummary());
    }

    /**
     * Get metrics summary
     */
    getMetricsSummary() {
        return {
            loadTime: this.metrics.loadTime || 0,
            firstPaint: this.metrics['first-paint'] || 0,
            firstContentfulPaint: this.metrics['first-contentful-paint'] || 0,
            largestContentfulPaint: this.metrics.largestContentfulPaint || 0,
            cumulativeLayoutShift: this.metrics.cumulativeLayoutShift || 0,
            memoryUsage: this.metrics.memory ? 
                Math.round((this.metrics.memory.used / 1024 / 1024) * 100) / 100 + ' MB' : 
                'Unknown'
        };
    }

    /**
     * Get performance score
     */
    getPerformanceScore() {
        let score = 100;
        
        // Deduct points for slow metrics
        if (this.metrics.loadTime > this.thresholds.loadTime) {
            score -= 20;
        }
        if (this.metrics['first-paint'] > this.thresholds.firstPaint) {
            score -= 15;
        }
        if (this.metrics.largestContentfulPaint > this.thresholds.largestContentfulPaint) {
            score -= 25;
        }
        if (this.metrics.cumulativeLayoutShift > this.thresholds.cumulativeLayoutShift) {
            score -= 20;
        }
        
        return Math.max(0, score);
    }

    /**
     * Get performance recommendations
     */
    getRecommendations() {
        const recommendations = [];
        
        if (this.metrics.loadTime > this.thresholds.loadTime) {
            recommendations.push('Consider optimizing resource loading');
        }
        if (this.metrics.largestContentfulPaint > this.thresholds.largestContentfulPaint) {
            recommendations.push('Optimize largest contentful paint');
        }
        if (this.metrics.cumulativeLayoutShift > this.thresholds.cumulativeLayoutShift) {
            recommendations.push('Reduce layout shifts');
        }
        
        return recommendations;
    }

    /**
     * Destroy performance optimizer
     */
    destroy() {
        Object.values(this.observers).forEach(observer => {
            if (observer && observer.disconnect) {
                observer.disconnect();
            }
        });
        
        console.log('🗑️ Performance Optimizer destroyed');
    }
}

// Initialize performance optimizer
const performanceOptimizer = new PerformanceOptimizer();

// Make available globally
window.performanceOptimizer = performanceOptimizer;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceOptimizer;
}