from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q, F

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
        summary="List Categories",
        description="Get all active categories with basic information and counts",
        responses={200: CategoryListSerializer(many=True)},
        tags=['Categories']
    ),
    retrieve=extend_schema(
        summary="Get Category Details", 
        description="Get detailed category information including parent, children, and breadcrumbs",
        responses={200: CategoryDetailSerializer},
        tags=['Categories']
    ),
    create=extend_schema(
        summary="Create Category",
        description="Create a new category (requires authentication)",
        request=CategoryCreateUpdateSerializer,
        responses={201: CategoryDetailSerializer},
        tags=['Categories']
    ),
    update=extend_schema(
        summary="Update Category",
        description="Update an existing category (requires authentication)", 
        request=CategoryCreateUpdateSerializer,
        responses={200: CategoryDetailSerializer},
        tags=['Categories']
    ),
    destroy=extend_schema(
        summary="Delete Category",
        description="Delete a category and all its subcategories (requires authentication)",
        responses={204: None},
        tags=['Categories']
    )
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD operations
    """
    
    queryset = Category.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateUpdateSerializer
        else:
            return CategoryDetailSerializer
    
    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True)
        
        if self.action == 'list':
            queryset = queryset.prefetch_related('children', 'products')
        elif self.action == 'retrieve':
            queryset = queryset.select_related('parent').prefetch_related('children__children')
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        
        def mark_children_inactive(category):
            for child in category.children.all():
                child.is_active = False
                child.save()
                mark_children_inactive(child)
        
        mark_children_inactive(instance)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        include_subcategories = request.query_params.get('include_subcategories', 'true').lower() == 'true'
        
        if include_subcategories:
            category_ids = [category.id] + self._get_descendant_ids(category)
            products = Product.objects.filter(
                category_id__in=category_ids,
                is_active=True
            ).select_related('category')
        else:
            products = category.products.filter(is_active=True).select_related('category')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    def _get_descendant_ids(self, category):
        descendant_ids = []
        for child in category.children.filter(is_active=True):
            descendant_ids.append(child.id)
            descendant_ids.extend(self._get_descendant_ids(child))
        return descendant_ids
    
    @action(detail=False, methods=['get'])
    def roots(self, request):
        root_categories = Category.objects.filter(
            parent=None, 
            is_active=True
        ).prefetch_related('children')
        
        serializer = CategoryListSerializer(root_categories, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List Products",
        description="Get all active products with filtering, search, and pagination",
        responses={200: ProductListSerializer(many=True)},
        tags=['Products']
    ),
    retrieve=extend_schema(
        summary="Get Product Details",
        description="Get detailed product information including category, stock status, and related products",
        responses={200: ProductDetailSerializer},
        tags=['Products']
    ),
    create=extend_schema(
        summary="Create Product",
        description="Create a new product (requires authentication)",
        request=ProductCreateUpdateSerializer,
        responses={201: ProductDetailSerializer},
        tags=['Products']
    ),
    update=extend_schema(
        summary="Update Product",
        description="Update an existing product (requires authentication)",
        request=ProductCreateUpdateSerializer,
        responses={200: ProductDetailSerializer},
        tags=['Products']
    ),
    destroy=extend_schema(
        summary="Delete Product",
        description="Delete a product (requires authentication)",
        responses={204: None},
        tags=['Products']
    )
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations with advanced filtering
    """
    
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'is_featured', 'availability_status']
    search_fields = ['name', 'description', 'short_description', 'brand', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'updated_at', 'stock_quantity']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        else:
            return ProductDetailSerializer
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        if self.action == 'list':
            queryset = queryset.select_related('category')
        elif self.action == 'retrieve':
            queryset = queryset.select_related('category__parent').prefetch_related('category__children')
        
        queryset = self._apply_custom_filters(queryset)
        return queryset
    
    def _apply_custom_filters(self, queryset):
        request = self.request
        
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        
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
        
        in_stock_only = request.query_params.get('in_stock_only')
        if in_stock_only and in_stock_only.lower() == 'true':
            queryset = queryset.filter(
                Q(track_inventory=False) | 
                Q(track_inventory=True, stock_quantity__gt=0)
            )
        
        on_sale = request.query_params.get('on_sale')
        if on_sale and on_sale.lower() == 'true':
            queryset = queryset.filter(
                discount_price__isnull=False,
                discount_price__lt=F('price')
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response(
                {'error': 'Search query parameter "q" is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        search_query = Q(name__icontains=query) | \
                      Q(description__icontains=query) | \
                      Q(brand__icontains=query) | \
                      Q(sku__icontains=query)
        
        products = Product.objects.filter(
            search_query,
            is_active=True
        ).select_related('category')
        
        products = self._apply_custom_filters(products)
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_products = Product.objects.filter(
            is_featured=True,
            is_active=True
        ).select_related('category')[:20]
        
        serializer = ProductListSerializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        product = self.get_object()
        
        recommendations = Product.objects.filter(
            Q(category=product.category) | Q(brand=product.brand),
            is_active=True
        ).exclude(id=product.id).select_related('category')[:8]
        
        serializer = ProductListSerializer(recommendations, many=True)
        return Response(serializer.data)