// Example: Update the cart item count dynamically using AJAX
document.addEventListener("DOMContentLoaded", function() {
    const cartCountElement = document.querySelector(".cart-count");
    
    // Example function to simulate an AJAX request to update the cart count
    function updateCartCount() {
        // Simulate a request for cart count, could be replaced with actual AJAX request
        let newCount = 5; // For example, you can fetch this from a Django view or API
        cartCountElement.textContent = `(${newCount})`;
    }

    // Call updateCartCount when the page loads
    updateCartCount();
});
