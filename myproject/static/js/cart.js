// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show notification function
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} animate__animated animate__fadeIn`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('animate__fadeIn');
        notification.classList.add('animate__fadeOut');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Update cart count with animation
function updateCartCount(count) {
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(element => {
        // Update the count
        element.textContent = count;
        
        // Add animation
        element.classList.add('animate__animated', 'animate__bounce');
        
        // Remove animation after it completes
        setTimeout(() => {
            element.classList.remove('animate__animated', 'animate__bounce');
        }, 1000);
        
        // Make sure the cart count is visible
        element.style.display = count > 0 ? 'flex' : 'none';
    });
}

// Add to cart function
function addToCart(productId, quantity = 1, button = null) {
    // If button is provided, show loading state
    if (button) {
        const originalHTML = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
        button.disabled = true;
    }

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            quantity: quantity
        })
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Show success message
            showNotification('Product added to cart successfully!');
            
            // Update cart count with the total from server
            if (data.cart_total !== undefined) {
                updateCartCount(data.cart_total);
            }

            // Update button state if provided
            if (button) {
                button.innerHTML = '<i class="fas fa-check"></i>';
                button.classList.add('btn-success');
                
                // Reset button after 2 seconds
                setTimeout(() => {
                    button.innerHTML = '<i class="fas fa-shopping-cart"></i>';
                    button.classList.remove('btn-success');
                    button.disabled = false;
                }, 2000);
            }
        } else {
            showNotification(data.error || 'Error adding product to cart', 'error');
            if (button) {
                button.innerHTML = '<i class="fas fa-shopping-cart"></i>';
                button.disabled = false;
            }
        }
    })
    .catch(error => {
        showNotification('Error adding product to cart', 'error');
        if (button) {
            button.innerHTML = '<i class="fas fa-shopping-cart"></i>';
            button.disabled = false;
        }
    });
}

// Initialize cart functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add to cart buttons in product listings
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            addToCart(productId, 1, this);
        });
    });

    // Add to cart button in product detail page
    const detailAddToCartBtn = document.getElementById('add-to-cart-btn');
    if (detailAddToCartBtn) {
        detailAddToCartBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const quantity = document.getElementById('quantity')?.value || 1;
            addToCart(productId, parseInt(quantity), this);
        });
    }

    // Quantity selector in product detail page
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        document.getElementById('increase-quantity')?.addEventListener('click', function() {
            const max = parseInt(quantityInput.max) || Infinity;
            if (parseInt(quantityInput.value) < max) {
                quantityInput.value = parseInt(quantityInput.value) + 1;
            }
        });

        document.getElementById('decrease-quantity')?.addEventListener('click', function() {
            if (parseInt(quantityInput.value) > 1) {
                quantityInput.value = parseInt(quantityInput.value) - 1;
            }
        });
    }
}); 