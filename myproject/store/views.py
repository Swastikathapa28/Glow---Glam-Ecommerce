from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
from .forms import RegisterrForm,ReviewForm,LoginForm,ForgetPasswordForm
from django.conf import settings
from .models import Product,CustomUser,Review,CartItem,Cart,Category
import random
import json
from django.contrib.auth.forms import SetPasswordForm
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib import messages

# Using the custom user model if defined
User = get_user_model()
from django.shortcuts import render
from .models import Product

# Define categories manually
CATEGORIES = [
    {"name": "Cleanser", "slug": "cleanser"},
    {"name": "Serum", "slug": "serum"},
    {"name": "Toner", "slug": "toner"},
    {"name": "Moisturizer", "slug": "moisturizer"},
    {"name": "Sunscreen", "slug": "sunscreen"},
    {"name": "Lip Product", "slug": "lip-product"},
    {"name": "Foundation", "slug": "foundations"},
    {"name": "Eye Product", "slug": "eye-product"},
]

def homepage(request):
    products = Product.objects.all()
    brands = Product.objects.values_list('brand', flat=True).distinct()

    
    return render(request, 'store/homepage.html', {
        'products': products,
        'categories': CATEGORIES,
        'brands':brands
    })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('store:home')
            else:
                form.add_error(None, 'Email and Password not matching')  # Add form error
    else:
        form = LoginForm()

    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('store:home')


def register_view(request):
    if request.method == 'POST':
        form = RegisterrForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']


            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
                return redirect('register')

            # Generate a 6-digit code
            verification_code = ''.join(random.choices('0123456789', k=6))

            # Save everything in session
            request.session['temp_user'] = {
                'full_name': full_name,
                'email': email,
                'password': password,
                'code': verification_code
            }

            # Send code via email
            send_mail(
                'Glow & Glam Verification Code',
                f'Your verification code is: {verification_code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Please check your email for the verification code.')
            return redirect('store:verify_code')

    else:
        form = RegisterrForm()
    return render(request, 'store/register.html', {'form': form})


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def verify_code_view(request):
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        temp_user = request.session.get('temp_user')

        if not temp_user:
            return JsonResponse({'success': False, 'error': 'Session expired. Please register again.'})

        if code == temp_user['code']:
            # Create the actual user
            user = CustomUser.objects.create(
                email=temp_user['email'],
                full_name=temp_user['full_name'],
                dob=temp_user['dob'],
            )
            user.set_password(temp_user['password'])
            user.save()

            del request.session['temp_user']
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Incorrect verification code.'})

    # Handle GET requests (render the form)
    return render(request, 'store/verify_code.html')

def resend_verification_code(request):
    temp_user = request.session.get('temp_user')
    if not temp_user:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('store:register')

    # Generate a new code
    new_code = ''.join(random.choices('0123456789', k=6))
    temp_user['code'] = new_code
    request.session['temp_user'] = temp_user

    send_mail(
        'Your New Verification Code',
        f'Your new verification code is: {new_code}',
        settings.DEFAULT_FROM_EMAIL,
        [temp_user['email']],
        fail_silently=False,
    )

    messages.success(request, 'New verification code sent to your email.')
    return redirect('store:verify_code')



def category_products(request, category_slug):
    # Get category object using slug
    category = get_object_or_404(Category, slug=category_slug)
    
    # Filter products by category
    products = Product.objects.filter(category=category)
    
    # Get selected brands (multiple possible)
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products = products.filter(brand__in=selected_brands)
    
    # Get price range from GET parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price and max_price:
        try:
            min_price = float(min_price)
            max_price = float(max_price)
            products = products.filter(discount_price__gte=min_price, discount_price__lte=max_price)
        except ValueError:
            pass  # if conversion fails, ignore price filter
    
    # Get all distinct brands for the sidebar
    brands = Product.objects.filter(category=category).values_list('brand', flat=True).distinct()
    
    # Pass all categories for the "Shop by Category" section
    categories = Category.objects.all()  # Fetch all categories
    
    context = {
        'products': products,
        'category': category_slug,  # Current category object for display
        'categories': categories,  # All categories for the "Shop by Category" section
        'brands': brands,
        'selected_brands': selected_brands,
        'selected_min_price': min_price or 0,
        'selected_max_price': max_price or 20000,
    }
    
    return render(request, 'store/category.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    rating_range = range(1, 6)
    # Handle Review Submission
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user  # assuming user is logged in
            review.save()
            return redirect('store:product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    # Example for related products (you can customize logic)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]


    context = {
        'product': product,
        'form': form,
        'related_products': related_products,
        'rating_range':rating_range
    }
    return render(request, 'store/product_detail.html', context)

@login_required
def view_cart(request):
    # Get or create a cart for the logged-in user
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    # Get product IDs and categories from cart
    product_ids = [item.product.id for item in cart_items]
    categories = list(set(item.product.category for item in cart_items if item.product.category))

    # Fetch related products
    related_products = Product.objects.filter(category__in=categories).exclude(id__in=product_ids)[:4]

    # Check for insufficient stock
    insufficient_stock_items = []
    for item in cart_items:
        if item.product.quantity < item.quantity:
            insufficient_stock_items.append({
                'product': item.product,
                'available_quantity': item.product.quantity,
                'requested_quantity': item.quantity
            })

    # Calculate total price
    total_price = sum(item.product.discount_price * item.quantity for item in cart_items)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'insufficient_stock_items': insufficient_stock_items,
        'related_products': related_products,
        'total_price': total_price,
    }

    return render(request, 'store/view_cart.html', context)

@login_required(login_url='store:login')  # Ensure the user is logged in
@csrf_exempt  # Exempt CSRF protection (use only if necessary)
def add_to_cart(request, product_id):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))

            # Get the product
            product = get_object_or_404(Product, id=product_id)

            # Check if there is enough stock
            if product.quantity < quantity:
                return JsonResponse({'success': False, 'error': 'Not enough stock'})

            # Get or create the cart for the user
            cart, created = Cart.objects.get_or_create(user=request.user)

            # Get or create the cart item
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                # If the item already exists in the cart, update the quantity
                cart_item.quantity += quantity
            else:
                # If it's a new item, set the quantity
                cart_item.quantity = quantity

            # Save the cart item
            cart_item.save()

            # Reduce the product quantity in the database
            product.quantity -= quantity
            product.save()

            # Return a success response
            return JsonResponse({'success': True})
        except Exception as e:
            # Return an error response if something goes wrong
            return JsonResponse({'success': False, 'error': str(e)})
    
    # If the request method is not POST, return an error response
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    product = cart_item.product  # Get the associated product
    old_quantity = cart_item.quantity  # Store the old quantity

    # Add the old quantity back to the product stock
    product.quantity += old_quantity
    product.save()

    # Remove the item from the cart
    cart_item.delete()

    messages.success(request, "Item removed from cart.")
    return redirect('store:view_cart')

@login_required
def update_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    product = cart_item.product  # Get the associated product
    old_quantity = cart_item.quantity  # Store the old quantity for later calculations
    new_quantity = int(request.POST.get('quantity', 1))

    if new_quantity > 0:
        # Calculate the difference between the new and old quantity
        quantity_difference = new_quantity - old_quantity

        # Check if there's enough stock for the update
        if product.quantity >= quantity_difference:
            # Update the product quantity
            product.quantity -= quantity_difference
            product.save()

            # Update the cart item quantity
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            # Handle insufficient stock (e.g., show an error message)
            messages.error(request, "Not enough stock available.")
            return redirect('store:view_cart')
    else:
        # If the new quantity is 0 or less, remove the item from the cart
        # Add the old quantity back to the product stock
        product.quantity += old_quantity
        product.save()
        cart_item.delete()

    return redirect('store:view_cart')

@login_required
def profile(request):
    """Display user profile"""
    return render(request, 'store/profile.html', {"user": request.user})

@login_required
def checkout(request):
    cart = Cart(request)

    if request.method == 'POST':
        # Get user information from form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')

        # Create the order
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            address=address,
            phone_number=phone_number,
            total_price=cart.get_total_price(),
        )

        # Create order items from cart
        for item in cart.cart.values():
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )

        # Clear the cart after successful order placement
        cart.clear()

        messages.success(request, 'Your order has been placed successfully!')
        return redirect('order_success')  # Redirect to the success page

    return render(request, 'store/checkout.html', {'cart': cart})

@login_required
def order_success(request):
    return render(request, 'store/order_success.html')

def search_results(request):
    query = request.GET.get('q', '')  # Get search query
    products = Product.objects.filter(name__icontains=query)  # Search products based on name
    return render(request, 'store/search_results.html', {'products': products, 'query': query})

def about_us(request):
    return render(request, 'store/about_us.html')

def contact_us(request):
    return render(request, 'store/contact_us.html')

def terms_condition(request):
    return render(request, 'store/terms_and_condition.html')

def order(request):
    return render(request, 'store/order.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Review
from .forms import ReviewForm

@login_required(login_url='store:login')  # Redirect to login page if user is not logged in
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Prevent duplicate reviews
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            if existing_review:
                messages.warning(request, "You have already reviewed this product.")
                return redirect('store:product_detail', product_id=product.id)

            # Save the review
            review = form.save(commit=False)
            review.product = product
            review.user = request.user  # Assign the logged-in user
            review.save()

            # Update the product's average rating (Ensure this method exists in the Product model)
            product.update_average_rating()

            messages.success(request, "Thank you for your review!")
            return redirect('store:product_detail', product_id=product.id)
        else:
            messages.error(request, "There was an error in your review submission.")

    return redirect('store:product_detail', product_id=product.id)



def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        review_text = request.POST.get('review_text')

        # Validate rating
        if rating < 1 or rating > 5:
            messages.error(request, 'Invalid rating. Please select a rating between 1 and 5.')
            return redirect('store:product_detail', product_id=review.product.id)

        # Update the review
        review.rating = rating
        review.review_text = review_text
        review.save()

        # Update the product's average rating
        review.product.update_average_rating()

        messages.success(request, 'Your review has been updated.')
        return redirect('store:product_detail', product_id=review.product.id)

    return redirect('store:product_detail', product_id=review.product.id)

def delete_review(request, review_id):
    # Ensure the user can only delete their own reviews
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id
    review.delete()

    # Notify the user
    messages.success(request, 'Your review has been deleted.')
    return redirect('store:product_detail', product_id=product_id)

import logging
from django.utils.html import strip_tags
logger = logging.getLogger(__name__)

def forgot_password(request):
    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                # Get the user associated with the email
                user = get_user_model().objects.get(email=email)
                
                # Create token and generate reset URL
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(str(user.pk).encode())
                reset_url = request.build_absolute_uri(reverse('store:reset_password', args=[uidb64, token]))

                # Render HTML and plain text versions of the email
                html_message = render_to_string('store/password_reset_email.html', {
                    'user': user,
                    'reset_url': reset_url,
                })
                plain_message = strip_tags(html_message)  # Plain text version

                # Send the reset email
                send_mail(
                    'Password Reset Request',
                    plain_message,
                    'no-reply@yourdomain.com',  # Replace with your email
                    [user.email],
                    html_message=html_message,  # Include HTML version
                )
                messages.success(request, "We've sent you an email with a link to reset your password.")
                return redirect('store:forgot_password')  # Redirect after sending email
                
            except get_user_model().DoesNotExist:
                messages.error(request, "This email address is not registered.")
                return redirect('store:forgot_password')
            except Exception as e:
                logger.error(f"Error sending password reset email: {e}")
                messages.error(request, "Something went wrong. Please try again.")
                return redirect('store:forgot_password')
    else:
        form = ForgetPasswordForm()

    # Render the forgot password form for GET requests
    return render(request, 'store/forgot_password.html', {'form': form})


def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)

        # Validate the token
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Your password has been reset successfully.')
                    return redirect('store:login')
            else:
                form = SetPasswordForm(user)

            return render(request, 'store/reset_password.html', {'form': form})
        else:
            messages.error(request, 'The reset link is invalid or expired.')
            return redirect('store:forgot_password')

    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        messages.error(request, 'Something went wrong. Please try again.')
        return redirect('store:forgot_password')


def shop_by_concern(request, concern):
    concern = concern.lower()
    products = Product.objects.all()
    filtered_products = [
        product for product in products
        if concern in [c.strip().lower() for c in product.best_for.split(',')]
    ]
    
    return render(request, 'store/shop_by_concern.html', {
        'concern': concern,
        'products': filtered_products,
    })