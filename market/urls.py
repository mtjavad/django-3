from django.urls import include, path
from . import views

urlpatterns = [
    path('market/product/insert/', views.product_store), 
    path('market/product/list/', views.product_index), 
    path('market/product/<int:pk>/', views.product_single),
    path('market/product/<int:pk>/edit_inventory/', views.product_update),
    path('accounts/customer/register/', views.customer_register),
    path('accounts/customer/list/', views.customer_index),
    path('accounts/customer/<int:pk>/', views.customer_single),
    path('accounts/customer/<int:pk>/edit/', views.customer_update),
    path('accounts/customer/login/', views.customer_login),
    path('accounts/customer/logout/', views.customer_logout),
    path('accounts/customer/profile/', views.customer_profile),
    path('market/shopping/cart/', views.cart_detail),
    path('market/shopping/cart/add_items/', views.cart_add_items),
    path('market/shopping/cart/remove_items/', views.cart_remove_items),
    path('market/shopping/submit/', views.cart_submit)
]
