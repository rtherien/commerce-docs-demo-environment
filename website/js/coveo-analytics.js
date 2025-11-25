// Coveo Analytics Integration
class CoveoAnalyticsManager {
    constructor(commerceInterface = null) {
        this.commerceInterface = commerceInterface;
        this.init();
    }

    init() {
        // Initialize Coveo Analytics if not already available
        if (typeof window.coveoAnalytics === 'undefined') {
            this.loadCoveoAnalytics();
        }
    }

    loadCoveoAnalytics() {
        // Coveo Analytics is typically included with the Atomic library
        // If needed, you can load it separately
        if (window.CoveoAnalytics) {
            window.coveoAnalytics = window.CoveoAnalytics.analytics;
        }
    }

    // Track product view events
    async trackProductView(product) {
        try {
            if (this.commerceInterface && this.commerceInterface.executeFirstRequest) {
                // Use Atomic Commerce Interface analytics
                await this.commerceInterface.analytics.logClick({
                    productId: product.id,
                    productName: product.name,
                    productPrice: product.price,
                    productBrand: product.brand
                });
            }
            console.log('Product view tracked:', product.name);
        } catch (error) {
            console.error('Error tracking product view:', error);
        }
    }

    // Track add to cart events
    async trackAddToCart(product) {
        try {
            if (this.commerceInterface && this.commerceInterface.analytics) {
                // Track add to cart event
                await this.commerceInterface.analytics.logAddToCart({
                    productId: product.id,
                    productName: product.name,
                    productPrice: product.price,
                    productBrand: product.brand,
                    quantity: 1,
                    currency: 'CAD'
                });
            }
            console.log('Add to cart tracked:', product.name);
        } catch (error) {
            console.error('Error tracking add to cart:', error);
        }
    }

    // Track purchase events
    async trackPurchase(cartItems, total, currency = 'CAD') {
        try {
            if (this.commerceInterface && this.commerceInterface.analytics) {
                // Track purchase event
                await this.commerceInterface.analytics.logPurchase({
                    total: total,
                    currency: currency,
                    products: cartItems.map(item => ({
                        productId: item.id,
                        sku: item.id,
                        productName: item.name,
                        brand: item.brand,
                        price: item.price,
                        quantity: item.quantity
                    }))
                });
            }
            console.log('Purchase tracked:', { total, currency, items: cartItems.length });
        } catch (error) {
            console.error('Error tracking purchase:', error);
        }
    }

    // Track search events
    async trackSearch(query, results = 0) {
        try {
            if (this.commerceInterface && this.commerceInterface.analytics) {
                await this.commerceInterface.analytics.logSearchEvent({
                    searchQueryUid: this.generateUID(),
                    query: query,
                    numberOfResults: results
                });
            }
            console.log('Search tracked:', query);
        } catch (error) {
            console.error('Error tracking search:', error);
        }
    }

    // Track facet selection
    async trackFacetSelect(facetField, facetValue) {
        try {
            if (this.commerceInterface && this.commerceInterface.analytics) {
                await this.commerceInterface.analytics.logInterfaceChange({
                    facetField: facetField,
                    facetValue: facetValue
                });
            }
            console.log('Facet selection tracked:', facetField, facetValue);
        } catch (error) {
            console.error('Error tracking facet selection:', error);
        }
    }

    // Track page view
    async trackPageView(pageType = 'search', url = window.location.href) {
        try {
            if (this.commerceInterface && this.commerceInterface.analytics) {
                await this.commerceInterface.analytics.logPageView({
                    pageUrl: url,
                    pageTitle: document.title,
                    pageType: pageType
                });
            }
            console.log('Page view tracked:', pageType, url);
        } catch (error) {
            console.error('Error tracking page view:', error);
        }
    }

    // Generate unique ID for tracking
    generateUID() {
        return 'uid_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    // Update commerce interface reference
    setCommerceInterface(commerceInterface) {
        this.commerceInterface = commerceInterface;
    }
}

// Global analytics manager
let analyticsManager;

// Initialize analytics
function initializeCoveoAnalytics(commerceInterface = null) {
    analyticsManager = new CoveoAnalyticsManager(commerceInterface);
    return analyticsManager;
}

// Convenience functions for tracking events
function trackProductViewEvent(product) {
    if (analyticsManager) {
        analyticsManager.trackProductView(product);
    }
}

function trackAddToCartEvent(product) {
    if (analyticsManager) {
        analyticsManager.trackAddToCart(product);
    }
}

function trackPurchaseEvent(cartItems, total, currency = 'CAD') {
    if (analyticsManager) {
        analyticsManager.trackPurchase(cartItems, total, currency);
    }
}

function trackSearchEvent(query, results = 0) {
    if (analyticsManager) {
        analyticsManager.trackSearch(query, results);
    }
}

function trackPageViewEvent(pageType = 'search', url = window.location.href) {
    if (analyticsManager) {
        analyticsManager.trackPageView(pageType, url);
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize analytics manager
    initializeCoveoAnalytics();
    
    // Make analytics manager globally available
    window.analyticsManager = analyticsManager;
    
    // Track initial page view
    trackPageViewEvent();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        CoveoAnalyticsManager, 
        initializeCoveoAnalytics,
        trackProductViewEvent,
        trackAddToCartEvent,
        trackPurchaseEvent,
        trackSearchEvent,
        trackPageViewEvent
    };
}