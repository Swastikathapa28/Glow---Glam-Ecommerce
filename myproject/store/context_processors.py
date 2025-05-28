from .models import Cart, CartItem

def cart_item_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            # Calculate total number of items (sum of quantities)
            total_items = sum(item.quantity for item in cart.items.all())
            return {'cart_item_count': total_items}
    return {'cart_item_count': 0} 