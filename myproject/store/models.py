
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Avg
from django.conf import settings
from django.utils.text import slugify

class Category(models.Model):
    name=models.CharField(max_length=20)
    slug=models.SlugField(unique=True, blank=True,default='')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug=slugify(self.name)
        super().save(*args, **kwargs)
   
class Product(models.Model):

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=2, decimal_places=1, default=0, editable=False)
    brand=models.CharField(max_length=20,default='')
    quantity = models.IntegerField(default=0)
    best_for=models.CharField(max_length=15,default="all")
    is_bestseller=models.BooleanField(default=False)

    def update_average_rating(self, save=False):
        avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        self.average_rating = round(avg_rating, 1) if avg_rating is not None else 0
        if save:
            super().save(update_fields=['average_rating'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def is_in_stock(self):
        return self.quantity > 0
    
    def __str__(self):
        return self.name

    def review_count(self):
        return self.reviews.count()

    @property
    def discount_percent(self):
        if self.original_price and self.discount_price:
            return round((self.original_price - self.discount_price) / self.original_price * 100)
        return 0

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.original_price



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name',]

    objects = CustomUserManager()

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
    )

    def __str__(self):
        return self.email


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=1)  # Rating between 1 to 5
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_average_rating(save=True)  # Update the product's rating when a review is saved

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.email}"




class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True) 
    
    def __str__(self):
        return f"Cart of {self.user.full_name}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"

    @property
    def total_price(self):
        return self.product.final_price * self.quantity
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"


class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} in {self.user.email}'s wishlist"

