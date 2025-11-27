"""
URL Configuration for Products API

This module defines the URL routes for the products app using Django REST Framework's DefaultRouter.
The router automatically generates URL patterns for ViewSets.

Endpoints:
-----------
Categories:
- GET    /api/v1/categories/                 - List all categories
- POST   /api/v1/categories/                 - Create new category (Admin)
- GET    /api/v1/categories/{id}/            - Get category details
- PUT    /api/v1/categories/{id}/            - Update category (Admin)
- PATCH  /api/v1/categories/{id}/            - Partial update category (Admin)
- DELETE /api/v1/categories/{id}/            - Delete category (Admin)
- GET    /api/v1/categories/{id}/products/   - Get products in category
- GET    /api/v1/categories/roots/           - Get root categories

Products:
- GET    /api/v1/products/                   - List all products
- POST   /api/v1/products/                   - Create new product (Admin)
- GET    /api/v1/products/{id}/              - Get product details
- PUT    /api/v1/products/{id}/              - Update product (Admin)
- PATCH  /api/v1/products/{id}/              - Partial update product (Admin)
- DELETE /api/v1/products/{id}/              - Delete product (Admin)
- GET    /api/v1/products/search/            - Search products (?q=query)
- GET    /api/v1/products/featured/          - Get featured products
- GET    /api/v1/products/{id}/recommendations/ - Get product recommendations

Query Parameters (Products List):
---------------------------------
- category: Filter by category ID
- brand: Filter by brand name
- is_featured: Filter featured products (true/false)
- availability_status: Filter by status (in_stock, out_of_stock, pre_order, discontinued)
- min_price: Minimum price filter
- max_price: Maximum price filter
- in_stock_only: Show only in-stock products (true/false)
- on_sale: Show only products on sale (true/false)
- search: Search in name, description, sku, brand
- ordering: Order results (price, -price, name, -name, created_at, -created_at)

Examples:
---------
# Get all products in Electronics category
GET /api/v1/products/?category=1

# Search for products
GET /api/v1/products/search/?q=laptop

# Get products on sale between $100-$500
GET /api/v1/products/?on_sale=true&min_price=100&max_price=500

# Get featured products
GET /api/v1/products/featured/

# Get product recommendations
GET /api/v1/products/123/recommendations/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
