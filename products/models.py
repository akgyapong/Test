from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(verbose_name="URL", help_text="URL-friendly version: mobile-phones-tablets", unique=True)
    
    # Self-referential: a category can have a parent category
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE, # If parent deleted, delete children too
        null=True, # Top-level categories have no parent
        blank=True, 
        related_name='children' # Access children via category.children.all()
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True) # Set once on creation
    updated_at = models.DateTimeField(auto_now=True) # Update on every save
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name'] # Order alphabetically by default
        
    def __str__(self):
        # Show full path: Electronics > Mobile Phones > Smartphones
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name


class Product(models.Model):
    STATUS_CHOICES = ( # Format: (value_stored_in_database, human_readable_label)
        ("in_stock", "In Stock"),
        ("out_of_stock", "Out of Stock"),
        ("pre_order", "Pre Order"),
        ("discontinued", "Discontinued")
    )
    
 
    # Basic Product Information
    name = models.CharField(verbose_name="Product Name", blank=False , help_text="e.g., iPhone 15 Pro Max", max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(help_text= "Full Product Description")
    short_description = models.TextField(help_text="Brief summary for listings", max_length=150)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(default="GHS", max_length=20)
    
    # Product Identity
    sku = models.CharField(max_length=50, unique=True)
    brand = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products') # Keep Category after product deletion
    
    # Inventory Management
    stock_quantity = models.IntegerField(help_text="How many in stock")
    low_stock_threshold = models.IntegerField(help_text="When to show 'Low Stock' warning")
    track_inventory = models.BooleanField(default=False)
    
    # Product Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=True)
    availability_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="out_of_stock")
    main_image = models.ImageField(upload_to='products/', storage=MediaCloudinaryStorage(), blank=True, null=True) # Save images at products/
    meta_title = models.CharField(max_length=50)
    meta_description = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at'] # Newest products first
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        
    def __str__(self):
        return self.name