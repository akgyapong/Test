from django.contrib import admin
from .models import Category, Product

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'created_at'] # For list view
    search_fields = ['name'] # Fields to search
    list_filter = ['is_active', 'created_at'] # Filter sidebar options
    prepopulated_fields = {'slug': ('name',)} # Auto-generate slug from name

admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'brand', 'category', 'stock_quantity', 'availability_status', 'is_active', 'is_featured']
    search_fields = ['name', 'category__name', 'brand']
    list_filter = ['category', 'availability_status', 'is_active', 'is_featured', 'brand', 'created_at']
    list_editable = ['is_active', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Product, ProductAdmin)
