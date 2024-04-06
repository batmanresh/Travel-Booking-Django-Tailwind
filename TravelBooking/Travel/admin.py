from django.contrib import admin
from .models import Product, Category, Vendor, ProductReview, ProductImages


class ProductImagesAdmin(admin.TabularInline):
    model=ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines=[ProductImagesAdmin]
    list_display = ['user', 'title','price','featured','product_status','product_image']

class CategoryAdmin(admin.ModelAdmin): 
    list_display = ['title']

class VendorAdmin(admin.ModelAdmin): 
    list_display = ['title', 'vendor_image']

class ProductReviewAdmin(admin.ModelAdmin): 
    list_display = ['user', 'product', 'review', 'rating']




admin.site.register(Product,ProductAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Vendor,VendorAdmin)
admin.site.register(ProductReview,ProductReviewAdmin)

