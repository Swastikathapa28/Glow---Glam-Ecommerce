from django import template
from store.models import CartItem  # Import the necessary models

register = template.Library()

@register.filter
def cart_total_price(cart_items):
    """Calculate total cart price"""
    return sum(item.product.price * item.quantity for item in cart_items)

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 

@register.filter
def subtract(value, arg):
    try:
        return value - arg
    except (TypeError, ValueError):
        return value 
