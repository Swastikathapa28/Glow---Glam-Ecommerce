document.addEventListener('DOMContentLoaded', function() {
    // Quantity Selector
    const decreaseBtn = document.getElementById('decrease-quantity');
    const increaseBtn = document.getElementById('increase-quantity');
    const quantityInput = document.getElementById('quantity');

    if (decreaseBtn && increaseBtn && quantityInput) {
        decreaseBtn.addEventListener('click', function() {
            if (parseInt(quantityInput.value) > 1) {
                quantityInput.value = parseInt(quantityInput.value) - 1;
            }
        });

        increaseBtn.addEventListener('click', function() {
            if (parseInt(quantityInput.value) < parseInt(quantityInput.max)) {
                quantityInput.value = parseInt(quantityInput.value) + 1;
            }
        });
    }

    // Add to Cart Button
    const addToCartBtn = document.getElementById('add-to-cart-btn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function() {
            const quantity = document.getElementById('quantity').value;
            const productId = addToCartBtn.dataset.productId || "{{ product.id }}";
            
            fetch("{% url 'store:add_to_cart' product.id %}", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": "{{ csrf_token }}"
                },
                body: JSON.stringify({
                    'product_id': productId,
                    'quantity': quantity
                })
            })
            .then(response => {
                if (response.status === 302) {  // Check for redirect (login required)
                    window.location.href = response.url;  // Redirect to the login page
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data.success) {
                    alert('Product added to cart');
                    window.location.href = "{% url 'store:view_cart' %}";
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                alert('Something went wrong. Please try again.');
            });
        });
    }

    // Star Rating System
    function initializeStarRatings(container = document) {
        // Main rating input
        container.querySelectorAll('.star').forEach(star => {
            star.addEventListener('click', () => {
                const rating = star.getAttribute('data-value');
                const form = star.closest('form');
                if (form) {
                    const input = form.querySelector('input[name="rating"]');
                    if (input) input.value = rating;
                }
                updateStarColors(rating, star.closest('.star-rating').querySelectorAll('.star'));
            });
        });

        // Edit review buttons
        container.querySelectorAll('.edit-review-btn').forEach(button => {
            button.addEventListener('click', () => {
                const reviewId = button.getAttribute('data-review-id');
                const editForm = document.getElementById(`edit-form-${reviewId}`);
                if (editForm) {
                    editForm.style.display = 'block';
                }
            });
        });

        // Cancel edit buttons
        container.querySelectorAll('.cancel-edit-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const reviewId = button.getAttribute('data-review-id');
                const editForm = document.getElementById(`edit-form-${reviewId}`);
                if (editForm) {
                    editForm.style.display = 'none';
                }
            });
        });
    }

    // Helper function to update star colors
    function updateStarColors(rating, stars) {
        stars.forEach(s => {
            if (s.getAttribute('data-value') <= rating) {
                s.style.color = '#ffc107'; // Highlight selected stars
            } else {
                s.style.color = '#e4e5e9'; // Reset unselected stars
            }
        });
    }

    // Initialize star ratings
    initializeStarRatings();

    // Initialize star ratings for dynamically loaded content (e.g., tabs)
    const reviewTab = document.getElementById('review-tab');
    if (reviewTab) {
        reviewTab.addEventListener('shown.bs.tab', function() {
            initializeStarRatings(document.getElementById('review'));
        });
    }
});