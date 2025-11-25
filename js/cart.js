// Cart Management System
class CartManager {
    constructor() {
        this.items = JSON.parse(localStorage.getItem('sportStoreCart') || '[]');
        this.isOpen = false;
        this.init();
    }

    init() {
        this.updateCartCount();
        this.renderCartItems();
        this.bindEvents();
    }

    bindEvents() {
        // Cart toggle
        const cartToggle = document.getElementById('cart-toggle');
        const cartSidebar = document.getElementById('cart-sidebar');
        const cartClose = document.getElementById('cart-close');
        const checkoutBtn = document.getElementById('checkout-btn');

        cartToggle?.addEventListener('click', () => this.toggleCart());
        cartClose?.addEventListener('click', () => this.closeCart());
        checkoutBtn?.addEventListener('click', () => this.checkout());

        // Close cart when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && !cartSidebar?.contains(e.target) && !cartToggle?.contains(e.target)) {
                this.closeCart();
            }
        });
    }

    toggleCart() {
        const cartSidebar = document.getElementById('cart-sidebar');
        this.isOpen = !this.isOpen;
        cartSidebar?.classList.toggle('open', this.isOpen);
        
        if (this.isOpen) {
            this.renderCartItems();
        }
    }

    closeCart() {
        const cartSidebar = document.getElementById('cart-sidebar');
        this.isOpen = false;
        cartSidebar?.classList.remove('open');
    }

    addItem(product) {
        const existingItem = this.items.find(item => item.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.items.push({
                id: product.id,
                name: product.name || 'Product',
                price: product.price || 0,
                image: product.image || '',
                brand: product.brand || '',
                quantity: 1
            });
        }
        
        this.saveCart();
        this.updateCartCount();
        this.renderCartItems();
        
        // Show success message
        this.showSuccessMessage(`${product.name || 'Product'} added to cart!`);
    }

    removeItem(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.saveCart();
        this.updateCartCount();
        this.renderCartItems();
    }

    updateQuantity(productId, newQuantity) {
        const item = this.items.find(item => item.id === productId);
        if (item) {
            if (newQuantity <= 0) {
                this.removeItem(productId);
            } else {
                item.quantity = newQuantity;
                this.saveCart();
                this.updateCartCount();
                this.renderCartItems();
            }
        }
    }

    updateCartCount() {
        const totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            cartCount.textContent = totalItems;
        }
    }

    getTotal() {
        return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    }

    renderCartItems() {
        const cartItemsContainer = document.getElementById('cart-items');
        const cartTotal = document.getElementById('cart-total');
        const checkoutBtn = document.getElementById('checkout-btn');

        if (!cartItemsContainer) return;

        if (this.items.length === 0) {
            cartItemsContainer.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">Your cart is empty</p>';
            if (checkoutBtn) checkoutBtn.disabled = true;
        } else {
            cartItemsContainer.innerHTML = this.items.map(item => `
                <div class="cart-item" data-product-id="${item.id}">
                    ${item.image ? `<img src="${item.image}" alt="${item.name}" class="cart-item-image">` : '<div class="cart-item-image" style="background: #f0f0f0;"></div>'}
                    <div class="cart-item-details">
                        <div class="cart-item-name">${item.name}</div>
                        <div class="cart-item-price">$${item.price.toFixed(2)}</div>
                        <div class="cart-item-quantity">
                            <button class="quantity-btn" onclick="cartManager.updateQuantity('${item.id}', ${item.quantity - 1})">-</button>
                            <span>${item.quantity}</span>
                            <button class="quantity-btn" onclick="cartManager.updateQuantity('${item.id}', ${item.quantity + 1})">+</button>
                        </div>
                    </div>
                    <button class="remove-item" onclick="cartManager.removeItem('${item.id}')">Remove</button>
                </div>
            `).join('');
            
            if (checkoutBtn) checkoutBtn.disabled = false;
        }

        if (cartTotal) {
            cartTotal.textContent = this.getTotal().toFixed(2);
        }
    }

    async checkout() {
        if (this.items.length === 0) {
            alert('Your cart is empty!');
            return;
        }

        // Simulate checkout process
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.textContent = 'Processing...';
            checkoutBtn.disabled = true;
        }

        try {
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Track purchase event with Coveo Analytics
            await this.trackPurchaseEvent();

            // Clear cart
            this.items = [];
            this.saveCart();
            this.updateCartCount();
            this.renderCartItems();

            this.showSuccessMessage('Thank you for your purchase! Order confirmed.', 5000);
            this.closeCart();

        } catch (error) {
            console.error('Checkout error:', error);
            alert('There was an error processing your order. Please try again.');
        } finally {
            if (checkoutBtn) {
                checkoutBtn.textContent = 'Complete Purchase';
                checkoutBtn.disabled = false;
            }
        }
    }

    async trackPurchaseEvent() {
        try {
            // Use the global analytics manager if available
            if (window.analyticsManager && window.analyticsManager.trackPurchase) {
                await window.analyticsManager.trackPurchase(
                    this.items, 
                    this.getTotal(), 
                    'CAD'
                );
            } else if (window.commerceInterface && window.commerceInterface.analytics) {
                // Fallback to direct commerce interface
                await window.commerceInterface.analytics.logPurchase({
                    total: this.getTotal(),
                    currency: 'CAD',
                    products: this.items.map(item => ({
                        productId: item.id,
                        sku: item.id,
                        productName: item.name,
                        brand: item.brand,
                        price: item.price,
                        quantity: item.quantity
                    }))
                });
            } else if (window.trackPurchaseEvent) {
                // Use global tracking function
                await window.trackPurchaseEvent(this.items, this.getTotal(), 'CAD');
            }

            console.log('Purchase event tracked successfully');
        } catch (error) {
            console.error('Error tracking purchase event:', error);
        }
    }

    saveCart() {
        localStorage.setItem('sportStoreCart', JSON.stringify(this.items));
    }

    showSuccessMessage(message, duration = 3000) {
        // Remove existing success messages
        const existingMessages = document.querySelectorAll('.success-message');
        existingMessages.forEach(msg => msg.remove());

        // Create new success message
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        
        // Insert at top of main content
        const mainContent = document.querySelector('.main-content') || document.body;
        mainContent.insertBefore(successDiv, mainContent.firstChild);

        // Remove after duration
        setTimeout(() => {
            successDiv.remove();
        }, duration);
    }

    // Get items for external use
    getItems() {
        return [...this.items];
    }

    // Clear cart externally
    clearCart() {
        this.items = [];
        this.saveCart();
        this.updateCartCount();
        this.renderCartItems();
    }
}

// Global cart manager instance
let cartManager;

// Initialize cart when page loads
function initializeCart(commerceInterface = null) {
    cartManager = new CartManager();
    
    // Store commerce interface reference for analytics
    if (commerceInterface) {
        window.commerceInterface = commerceInterface;
    }
    
    return cartManager;
}

// Global function to add product to cart (used by onclick handlers)
function addProductToCart(product) {
    if (cartManager) {
        cartManager.addItem(product);
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CartManager, initializeCart, addProductToCart };
}