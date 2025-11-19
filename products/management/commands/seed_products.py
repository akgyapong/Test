from django.core.management.base import BaseCommand
from products.models import Category, Product
from django.utils.text import slugify
import random

CATEGORY_STRUCTURE = {
    "Electronics": {
        "Mobile Phones & Tablets": [
            "Smartphones", "Feature Phones", "Tablets", 
            "Mobile Accessories", "Phone Cases & Covers"
        ],
        "Computers & Accessories": [
            "Laptops", "Desktops", "Printers & Scanners", "Monitors"
        ],
        # Add more as needed...
    },
    "Home & Kitchen": {
        "Home Appliances": [
            "Refrigerators", "Freezers", "Washing Machines"
        ],
    }
}


class Command(BaseCommand):
    help = 'Seeds the database with the categories and products'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting to seed database...')
        
        # Always clear existing
        Category.objects.all().delete()
        Product.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))


