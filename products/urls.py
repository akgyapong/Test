from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for automatic URL generation
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')

# This automatically creates:
# 
# CATEGORY ENDPOINTS:
# GET    /categories/          -> list categories
# POST   /categories/          -> create category  
# GET    /categories/{id}/     -> get category details
# PUT    /categories/{id}/     -> update category
# DELETE /categories/{id}/     -> delete category
# GET    /categories/{id}/products/ -> category products (custom action)
# GET    /categories/roots/    -> root categories (custom action)
#
# PRODUCT ENDPOINTS:
# GET    /products/            -> list products
# POST   /products/            -> create product
# GET    /products/{id}/       -> get product details  
# PUT    /products/{id}/       -> update product
# DELETE /products/{id}/       -> delete product
# GET    /products/search/     -> search products (custom action)
# GET    /products/featured/   -> featured products (custom action)
# GET    /products/{id}/recommendations/ -> product recommendations (custom action)

urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    
    # Additional custom URLs can be added here if needed
    # path('custom-endpoint/', views.custom_view, name='custom-endpoint'),
]

# =============================================================================
# COMPLETE API ENDPOINTS:
# =============================================================================
# 
# Category Management:
#   GET    /api/v1/categories/              -> List all categories (with filtering & search)
#   POST   /api/v1/categories/              -> Create new category (auth required)
#   GET    /api/v1/categories/{id}/         -> Get category details + breadcrumbs
#   PUT    /api/v1/categories/{id}/         -> Update category (auth required)
#   DELETE /api/v1/categories/{id}/         -> Delete category (auth required)
#   GET    /api/v1/categories/roots/        -> Get root categories only
#   GET    /api/v1/categories/{id}/products/ -> Get products in category
# 
# Product Management:
#   GET    /api/v1/products/                -> List all products (with extensive filtering)
#   POST   /api/v1/products/                -> Create new product (auth required)
#   GET    /api/v1/products/{id}/           -> Get product details + related info
#   PUT    /api/v1/products/{id}/           -> Update product (auth required)
#   DELETE /api/v1/products/{id}/           -> Delete product (auth required)
#   GET    /api/v1/products/search/?q=term  -> Advanced product search
#   GET    /api/v1/products/featured/       -> Get featured products
#   GET    /api/v1/products/{id}/recommendations/ -> Get recommended products
# 
# Advanced Filtering Examples:
#   /api/v1/products/?category=1&brand=Apple&min_price=100&max_price=500
#   /api/v1/products/?search=iphone&ordering=-price&is_featured=true
#   /api/v1/products/?on_sale=true&in_stock_only=true
#   /api/v1/categories/?parent=null&search=electronics
# 
# =============================================================================