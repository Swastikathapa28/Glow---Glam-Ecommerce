document.addEventListener('DOMContentLoaded', function() {
    const addToCartButtons = document.querySelectorAll('.btn-pink[type="submit"]');
    const cartCount = document.querySelector('.cart-count');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Animation for visual feedback
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
            setTimeout(() => {
                this.innerHTML = 'Added!';
                setTimeout(() => {
                    this.innerHTML = 'Add to Cart';
                }, 1000);
            }, 500);
            
            // Update cart count if element exists
            if (cartCount) {
                let currentCount = parseInt(cartCount.textContent) || 0;
                cartCount.textContent = currentCount + 1;
                
                // Animation for cart count
                cartCount.style.transform = 'scale(1.5)';
                setTimeout(() => {
                    cartCount.style.transform = 'scale(1)';
                }, 300);
            }
        });
    });
});