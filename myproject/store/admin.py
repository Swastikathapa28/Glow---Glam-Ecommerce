from django.contrib import admin
from .models import Product,Review,Category,Cart,CartItem
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django import forms
from . import models


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'original_price', 'discount_price', 'image','quantity', 'rating', 'total_reviews')  # shows these columns in admin list view
    search_fields = ('name',)                        # adds a search box for 'name'
    list_filter = ('original_price',)                         # adds a filter sidebar for 'price'
    list_editable = ('original_price','image', 'quantity','name') 
    def rating(self, obj):
        # Calculate the average rating for this product based on reviews
        reviews = Review.objects.filter(product=obj)
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            return round(avg_rating, 2)  # Return the average rating, rounded to 2 decimal places
        return 'No reviews yet'

    def total_reviews(self, obj):
        # Return the total number of reviews for this product
        return Review.objects.filter(product=obj).count()

admin.site.register(Product, ProductAdmin)



try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass  # Do nothing if CustomUser is not registered yet

class CustomUserAdmin(UserAdmin):

    model = CustomUser
    list_display = ('email', 'full_name', 'is_verified', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified')

    fieldsets = (
        (None, {'fields': ('email', 'full_name', 'password')}),  # email appears here
        ('Personal info', {'fields': ('first_name', 'last_name')}),  # Removed duplicate email
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')
        }),
    )

    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')

admin.site.register(Review, ReviewAdmin)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'total_price')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')

@admin.register(Category)
class Category(admin.ModelAdmin):
    list_display = ('name','slug')

