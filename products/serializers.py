from rest_framework import serializers
from .models import Category, Product


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for Category list view - lightweight for performance
    
    Used for: GET /api/v1/categories/
    Purpose: Fast loading of category lists with essential info only
    """
    children_count = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 
            'parent', 'is_active', 'children_count', 
            'product_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'children_count', 'product_count']
    
    def get_children_count(self, obj):
        """Get count of direct child categories"""
        return obj.children.filter(is_active=True).count()
    
    def get_product_count(self, obj):
        """Get count of active products in this category"""
        return obj.products.filter(is_active=True).count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Category detail view - includes nested relationships
    
    Used for: GET /api/v1/categories/{id}/
    Purpose: Complete category information with parent/children details
    """
    parent = CategoryListSerializer(read_only=True)
    children = CategoryListSerializer(many=True, read_only=True)
    product_count = serializers.SerializerMethodField()
    breadcrumbs = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 
            'children', 'is_active', 'product_count', 
            'breadcrumbs', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_product_count(self, obj):
        """Get count of active products in this category and all subcategories"""
        # Get products from this category and all descendant categories
        descendant_ids = self._get_descendant_ids(obj)
        return Product.objects.filter(
            category_id__in=descendant_ids + [obj.id],
            is_active=True
        ).count()
    
    def get_breadcrumbs(self, obj):
        """Generate breadcrumb trail: Home > Electronics > Smartphones"""
        breadcrumbs = []
        current = obj
        while current:
            breadcrumbs.insert(0, {
                'id': current.id,
                'name': current.name,
                'slug': current.slug
            })
            current = current.parent
        return breadcrumbs
    
    def _get_descendant_ids(self, category):
        """Recursively get all descendant category IDs"""
        descendant_ids = []
        for child in category.children.filter(is_active=True):
            descendant_ids.append(child.id)
            descendant_ids.extend(self._get_descendant_ids(child))
        return descendant_ids


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Category create/update operations
    
    Used for: POST /api/v1/categories/, PUT /api/v1/categories/{id}/
    Purpose: Handle category creation and updates with validation
    """
    
    class Meta:
        model = Category
        fields = [
            'name', 'slug', 'description', 'parent', 'is_active'
        ]
    
    def validate_name(self, value):
        """
        Validate category name
        """
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Category name must be at least 2 characters long."
            )
        return value.strip()
    
    def validate_parent(self, value):
        """
        Validate parent category to prevent circular references
        """
        if value and self.instance:
            # Check if trying to set parent to self
            if value.id == self.instance.id:
                raise serializers.ValidationError(
                    "A category cannot be its own parent."
                )
            
            # Check for circular reference (parent cannot be descendant)
            if self._is_descendant(self.instance, value):
                raise serializers.ValidationError(
                    "Cannot set parent to a descendant category. This would create a circular reference."
                )
        
        return value
    
    def _is_descendant(self, ancestor, potential_descendant):
        """
        Check if potential_descendant is a descendant of ancestor
        """
        current = potential_descendant.parent
        while current:
            if current.id == ancestor.id:
                return True
            current = current.parent
        return False
    
    def validate(self, data):
        """
        Cross-field validation
        """
        name = data.get('name', '')
        slug = data.get('slug', '')
        
        # Auto-generate slug if not provided
        if name and not slug:
            from django.utils.text import slugify
            data['slug'] = slugify(name)
        
        # Check slug uniqueness
        slug = data.get('slug')
        if slug:
            queryset = Category.objects.filter(slug=slug)
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            if queryset.exists():
                raise serializers.ValidationError({
                    'slug': 'A category with this slug already exists.'
                })
        
        return data


# =============================================================================
# PRODUCT SERIALIZERS
# =============================================================================

class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for Product list view - optimized for performance
    
    Used for: GET /api/v1/products/
    Purpose: Fast loading of product listings with essential info
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    is_on_sale = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price', 
            'discount_price', 'currency', 'sku', 'brand',
            'category_name', 'category_slug', 'is_on_sale', 
            'discount_percentage', 'stock_status', 'availability_status',
            'main_image', 'is_featured', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'is_on_sale', 'discount_percentage', 
            'stock_status', 'category_name', 'category_slug'
        ]
    
    def get_is_on_sale(self, obj):
        """Check if product is on sale"""
        return obj.discount_price and obj.discount_price < obj.price
    
    def get_discount_percentage(self, obj):
        """Calculate discount percentage"""
        if obj.discount_price and obj.discount_price < obj.price:
            return round(((obj.price - obj.discount_price) / obj.price) * 100)
        return 0
    
    def get_stock_status(self, obj):
        """Get human-readable stock status"""
        if not obj.track_inventory:
            return "unlimited"
        elif obj.stock_quantity <= 0:
            return "out_of_stock"
        elif obj.stock_quantity <= obj.low_stock_threshold:
            return "low_stock"
        else:
            return "in_stock"


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Product detail view - complete information
    
    Used for: GET /api/v1/products/{id}/
    Purpose: Full product details with all relationships
    """
    category = CategoryListSerializer(read_only=True)
    category_breadcrumbs = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'price', 'discount_price', 'currency', 'sku', 'brand',
            'category', 'category_breadcrumbs', 'stock_quantity', 
            'low_stock_threshold', 'track_inventory', 'is_active',
            'is_featured', 'availability_status', 'main_image',
            'meta_title', 'meta_description', 'is_on_sale',
            'discount_percentage', 'stock_status', 'related_products',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'is_on_sale',
            'discount_percentage', 'stock_status', 'category_breadcrumbs',
            'related_products'
        ]
    
    def get_category_breadcrumbs(self, obj):
        """Generate category breadcrumb trail"""
        breadcrumbs = []
        current = obj.category
        while current:
            breadcrumbs.insert(0, {
                'id': current.id,
                'name': current.name,
                'slug': current.slug
            })
            current = current.parent
        return breadcrumbs
    
    def get_is_on_sale(self, obj):
        """Check if product is on sale"""
        return obj.discount_price and obj.discount_price < obj.price
    
    def get_discount_percentage(self, obj):
        """Calculate discount percentage"""
        if obj.discount_price and obj.discount_price < obj.price:
            return round(((obj.price - obj.discount_price) / obj.price) * 100)
        return 0
    
    def get_stock_status(self, obj):
        """Get detailed stock status"""
        if not obj.track_inventory:
            return {
                'status': 'unlimited',
                'message': 'Always available',
                'quantity': None
            }
        elif obj.stock_quantity <= 0:
            return {
                'status': 'out_of_stock',
                'message': 'Currently out of stock',
                'quantity': 0
            }
        elif obj.stock_quantity <= obj.low_stock_threshold:
            return {
                'status': 'low_stock',
                'message': f'Only {obj.stock_quantity} left in stock',
                'quantity': obj.stock_quantity
            }
        else:
            return {
                'status': 'in_stock',
                'message': f'{obj.stock_quantity} items available',
                'quantity': obj.stock_quantity
            }
    
    def get_related_products(self, obj):
        """Get related products from same category"""
        related = Product.objects.filter(
            category=obj.category,
            is_active=True
        ).exclude(id=obj.id)[:4]  # Limit to 4 related products
        
        return ProductListSerializer(related, many=True).data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Product create/update operations
    
    Used for: POST /api/v1/products/, PUT /api/v1/products/{id}/
    Purpose: Handle product creation and updates with comprehensive validation
    """
    
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'short_description',
            'price', 'discount_price', 'currency', 'sku', 'brand',
            'category', 'stock_quantity', 'low_stock_threshold',
            'track_inventory', 'is_active', 'is_featured',
            'availability_status', 'main_image', 'meta_title',
            'meta_description'
        ]
    
    def validate_name(self, value):
        """Validate product name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Product name must be at least 2 characters long."
            )
        return value.strip()
    
    def validate_price(self, value):
        """Validate product price"""
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )
        return value
    
    def validate_discount_price(self, value):
        """Validate discount price"""
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "Discount price must be greater than 0."
            )
        return value
    
    def validate_sku(self, value):
        """Validate SKU uniqueness"""
        if not value:
            raise serializers.ValidationError("SKU is required.")
            
        queryset = Product.objects.filter(sku=value)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "A product with this SKU already exists."
            )
        
        return value
    
    def validate_stock_quantity(self, value):
        """Validate stock quantity"""
        if value < 0:
            raise serializers.ValidationError(
                "Stock quantity cannot be negative."
            )
        return value
    
    def validate_low_stock_threshold(self, value):
        """Validate low stock threshold"""
        if value < 0:
            raise serializers.ValidationError(
                "Low stock threshold cannot be negative."
            )
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # Auto-generate slug if not provided
        name = data.get('name', '')
        slug = data.get('slug', '')
        
        if name and not slug:
            from django.utils.text import slugify
            data['slug'] = slugify(name)
        
        # Check slug uniqueness
        slug = data.get('slug')
        if slug:
            queryset = Product.objects.filter(slug=slug)
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            if queryset.exists():
                raise serializers.ValidationError({
                    'slug': 'A product with this slug already exists.'
                })
        
        # Validate discount price vs regular price
        price = data.get('price')
        discount_price = data.get('discount_price')
        
        if price and discount_price and discount_price >= price:
            raise serializers.ValidationError({
                'discount_price': 'Discount price must be less than regular price.'
            })
        
        # Validate stock settings
        track_inventory = data.get('track_inventory', True)
        stock_quantity = data.get('stock_quantity', 0)
        
        if track_inventory and stock_quantity <= 0:
            # Auto-set availability based on stock
            data['availability_status'] = 'out_of_stock'
        elif not track_inventory:
            # Unlimited inventory
            data['availability_status'] = 'in_stock'
        
        return data


 
    """
    Serializer for Category list view - lightweight for performance
    
    Used for: GET /api/v1/categories/
    Purpose: Fast loading of category lists with essential info only
    """
    children_count = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 
            'parent', 'is_active', 'children_count', 
            'product_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'children_count', 'product_count']
    
    def get_children_count(self, obj):
        """Get count of direct child categories"""
        return obj.children.filter(is_active=True).count()
    
    def get_product_count(self, obj):
        """Get count of active products in this category"""
        return obj.products.filter(is_active=True).count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Category detail view - includes nested relationships
    
    Used for: GET /api/v1/categories/{id}/
    Purpose: Complete category information with parent/children details
    """
    parent = CategoryListSerializer(read_only=True)
    children = CategoryListSerializer(many=True, read_only=True)
    product_count = serializers.SerializerMethodField()
    breadcrumbs = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 
            'children', 'is_active', 'product_count', 
            'breadcrumbs', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_product_count(self, obj):
        """Get count of active products in this category and all subcategories"""
        # Get products from this category and all descendant categories
        descendant_ids = self._get_descendant_ids(obj)
        return Product.objects.filter(
            category_id__in=descendant_ids + [obj.id],
            is_active=True
        ).count()
    
    def get_breadcrumbs(self, obj):
        """Generate breadcrumb trail: Home > Electronics > Smartphones"""
        breadcrumbs = []
        current = obj
        while current:
            breadcrumbs.insert(0, {
                'id': current.id,
                'name': current.name,
                'slug': current.slug
            })
            current = current.parent
        return breadcrumbs
    
    def _get_descendant_ids(self, category):
        """Recursively get all descendant category IDs"""
        descendant_ids = []
        for child in category.children.filter(is_active=True):
            descendant_ids.append(child.id)
            descendant_ids.extend(self._get_descendant_ids(child))
        return descendant_ids


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Category create/update operations
    
    Used for: POST /api/v1/categories/, PUT /api/v1/categories/{id}/
    Purpose: Handle category creation and updates with validation
    """
    
    class Meta:
        model = Category
        fields = [
            'name', 'slug', 'description', 'parent', 'is_active'
        ]
    
    def validate_name(self, value):
        """
        Validate category name
        """
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Category name must be at least 2 characters long."
            )
        return value.strip()
    
    def validate_parent(self, value):
        """
        Validate parent category to prevent circular references
        """
        if value and self.instance:
            # Check if trying to set parent to self
            if value.id == self.instance.id:
                raise serializers.ValidationError(
                    "A category cannot be its own parent."
                )
            
            # Check for circular reference (parent cannot be descendant)
            if self._is_descendant(self.instance, value):
                raise serializers.ValidationError(
                    "Cannot set parent to a descendant category. This would create a circular reference."
                )
        
        return value
    
    def _is_descendant(self, ancestor, potential_descendant):
        """
        Check if potential_descendant is a descendant of ancestor
        """
        current = potential_descendant.parent
        while current:
            if current.id == ancestor.id:
                return True
            current = current.parent
        return False
    
    def validate(self, data):
        """
        Cross-field validation
        """
        name = data.get('name', '')
        slug = data.get('slug', '')
        
        # Auto-generate slug if not provided
        if name and not slug:
            from django.utils.text import slugify
            data['slug'] = slugify(name)
        
        # Check slug uniqueness
        slug = data.get('slug')
        if slug:
            queryset = Category.objects.filter(slug=slug)
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            if queryset.exists():
                raise serializers.ValidationError({
                    'slug': 'A category with this slug already exists.'
                })
        
        return data


