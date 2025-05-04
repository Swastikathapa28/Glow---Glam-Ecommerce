
from django.urls import path
from . import views

app_name ='store'

urlpatterns = [
    path('', views.homepage, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),  
    path('verify_code/', views.verify_code_view, name='verify_code'),
    path('resend/', views.resend_verification_code, name='resend_verification_code'),
    path('category/<slug:category_slug>/', views.category_products, name='category_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('profile/',views.profile,name='profile'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_checkout, name='process_checkout'),
    path('order/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('search/', views.search_results, name='search_results'), 
    path('order/', views.order, name='order'),
    path('about_us/', views.about_us, name='about_us'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('terms/', views.terms_condition, name='terms_condition'),
    path('product/<int:product_id>/add-review/', views.add_review, name='add_review'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('edit_review/<int:review_id>/',views.edit_review,name='edit_review'),
    path('delete_review/<int:review_id>/',views.delete_review,name='delete_review'),
]

