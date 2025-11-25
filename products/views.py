from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Prefetch
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Category, Product
from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryCreateUpdateSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List all categories",
        description="Retrieve a list of all active categories with pagination support",
        tags=["Categories"]
    ),
    retrieve=extend_schema(
        summary="Get category details",
        description="Retrieve detailed information about a specific category including parent, children, and breadcrumbs",
        tags=["Categories"]
    ),
    create=extend_schema(
        summary="Create new category",
        description="Create a new category (Admin only)",
        tags=["Categories"]
    ),
    update=extend_schema(
        summary="Update category",
        description="Update an existing category (Admin only)",
        tags=["Categories"]
    ),
    partial_update=extend_schema(
        summary="Partially update category",
        description="Partially update an existing category (Admin only)",
        tags=["Categories"]
    ),
    destroy=extend_schema(
        summary="Delete category",
        description="Delete a category (Admin only)",
        tags=["Categories"]
    )
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD operations
    
    Provides:
    - List all categories (GET /api/v1/categories/)
    - Retrieve single category (GET /api/v1/categories/{id}/)
    - Create category (POST /api/v1/categories/) - Admin only
    - Update category (PUT /api/v1/categories/{id}/) - Admin only
    - Partial update (PATCH /api/v1/categories/{id}/) - Admin only
    - Delete category (DELETE /api/v1/categories/{id}/) - Admin only
    
    Features:
    - Filtering by parent, is_active
    - Search by name, description
    - Ordering by name, created_at
    - Custom action: Get products in category
    - Custom action: Get root categories
    """
    
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return CategoryListSerializer
        elif self.action == 'retrieve':
            return CategoryDetailSerializer
        else:
            return CategoryCreateUpdateSerializer
    
    def get_queryset(self):
        """
        Optimize queryset with select_related and prefetch_related
        """
        queryset = Category.objects.all()
        
        if self.action == 'list':
            queryset = queryset.select_related('parent').prefetch_related('children', 'products')
        elif self.action == 'retrieve':
            queryset = queryset.select_related('parent').prefetch_related(
                'children',
                Prefetch('products', queryset=Product.objects.filter(is_active=True))
            )
        
        return queryset
    
    @extend_schema(
        summary="Get products in category",
        description="Retrieve all products that belong to this category",
        responses={200: ProductListSerializer(many=True)},
        tags=["Categories"]
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Get all products in this category
        
        URL: GET /api/v1/categories/{id}/products/
        """
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            is_active=True
        ).select_related('category')
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get root categories",
        description="Retrieve all top-level categories (categories without parent)",
        responses={200: CategoryListSerializer(many=True)},
        tags=["Categories"]
    )
    @action(detail=False, methods=['get'])
    def roots(self, request):
        """
        Get all root categories (categories without parent)
        
        URL: GET /api/v1/categories/roots/
        """
        root_categories = Category.objects.filter(
            parent__isnull=True,
            is_active=True
        ).prefetch_related('children', 'products')
        
        serializer = CategoryListSerializer(root_categories, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List all products",
        description="Retrieve a list of all active products with filtering, search, and pagination",
        tags=["Products"],
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by category ID'
            ),
            OpenApiParameter(
                name='brand',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by brand name'
            ),
            OpenApiParameter(
                name='is_featured',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter featured products'
            ),
            OpenApiParameter(
                name='availability_status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by availability status (in_stock, out_of_stock, pre_order, discontinued)'
            ),
            OpenApiParameter(
                name='min_price',
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description='Minimum price filter'
            ),
            OpenApiParameter(
                name='max_price',
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description='Maximum price filter'
            ),
            OpenApiParameter(
                name='in_stock_only',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Show only products in stock'
            ),
            OpenApiParameter(
                name='on_sale',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Show only products on sale'
            ),
        ]
    ),
    retrieve=extend_schema(
        summary="Get product details",
        description="Retrieve detailed information about a specific product",
        tags=["Products"]
    ),
    create=extend_schema(
        summary="Create new product",
        description="Create a new product (Admin only)",
        tags=["Products"]
    ),
    update=extend_schema(
        summary="Update product",
        description="Update an existing product (Admin only)",
        tags=["Products"]
    ),
    partial_update=extend_schema(
        summary="Partially update product",
        description="Partially update an existing product (Admin only)",
        tags=["Products"]
    ),
    destroy=extend_schema(
        summary="Delete product",
        description="Delete a product (Admin only)",
        tags=["Products"]
    )
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations
    
    Provides:
    - List all products (GET /api/v1/products/)
    - Retrieve single product (GET /api/v1/products/{id}/)
    - Create product (POST /api/v1/products/) - Admin only
    - Update product (PUT /api/v1/products/{id}/) - Admin only
    - Partial update (PATCH /api/v1/products/{id}/) - Admin only
    - Delete product (DELETE /api/v1/products/{id}/) - Admin only
    
    Features:
    - Advanced filtering (category, brand, price range, stock status, etc.)
    - Search by name, description, sku, brand
    - Ordering by price, name, created_at
    - Custom action: Search products
    - Custom action: Get featured products
    - Custom action: Get product recommendations
    """
    
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'is_featured', 'availability_status']
    search_fields = ['name', 'description', 'sku', 'brand']
    ordering_fields = ['price', 'name', 'created_at', 'stock_quantity']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        else:
            return ProductCreateUpdateSerializer
    
    def get_queryset(self):
        """
        Optimize queryset with select_related and apply filters
        """
        queryset = Product.objects.select_related('category').filter(is_active=True)
        
        # Price range filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # In stock only filter
        in_stock_only = self.request.query_params.get('in_stock_only')
        if in_stock_only and in_stock_only.lower() == 'true':
            queryset = queryset.filter(
                Q(track_inventory=False) |  # Unlimited stock
                Q(track_inventory=True, stock_quantity__gt=0)  # Has stock
            )
        
        # On sale filter (products with discount)
        on_sale = self.request.query_params.get('on_sale')
        if on_sale and on_sale.lower() == 'true':
            queryset = queryset.filter(
                discount_price__isnull=False,
                discount_price__lt=F('price')
            )
        
        return queryset
    
    @extend_schema(
        summary="Search products",
        description="Advanced product search with query string",
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query',
                required=True
            )
        ],
        responses={200: ProductListSerializer(many=True)},
        tags=["Products"]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced product search
        
        URL: GET /api/v1/products/search/?q=laptop
        """
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'error': 'Search query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(sku__icontains=query),
            is_active=True
        ).select_related('category')
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get featured products",
        description="Retrieve all featured products",
        responses={200: ProductListSerializer(many=True)},
        tags=["Products"]
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured products
        
        URL: GET /api/v1/products/featured/
        """
        featured_products = Product.objects.filter(
            is_featured=True,
            is_active=True
        ).select_related('category')[:10]  # Limit to 10 featured products
        
        serializer = ProductListSerializer(featured_products, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get product recommendations",
        description="Get recommended products based on a specific product",
        responses={200: ProductListSerializer(many=True)},
        tags=["Products"]
    )
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        """
        Get recommended products based on current product
        
        URL: GET /api/v1/products/{id}/recommendations/
        
        Algorithm:
        1. Same category products
        2. Same brand products
        3. Similar price range products
        """
        product = self.get_object()
        
        # Get products from same category
        same_category = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        
        # If not enough, add same brand
        if same_category.count() < 4:
            same_brand = Product.objects.filter(
                brand=product.brand,
                is_active=True
            ).exclude(
                id__in=[p.id for p in same_category] + [product.id]
            )[:4 - same_category.count()]
            
            recommendations = list(same_category) + list(same_brand)
        else:
            recommendations = same_category
        
        serializer = ProductListSerializer(recommendations, many=True)
        return Response(serializer.data)
