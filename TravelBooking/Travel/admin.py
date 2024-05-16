from django.contrib import admin
from .models import Product, Category, Vendor, ProductReview, ProductImages,Booking,ContactMessage, OTP


class ProductImagesAdmin(admin.TabularInline):
    model=ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines=[ProductImagesAdmin]
    list_display = ['user', 'title','price','featured','product_status','product_image']

class CategoryAdmin(admin.ModelAdmin): 
    list_display = ['title']

class VendorAdmin(admin.ModelAdmin): 
    list_display = ['title','address','contact']

class ProductReviewAdmin(admin.ModelAdmin): 
    list_display = ['user', 'product', 'review', 'rating']

class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'check_in_date',
                    'num_guests', 'total_price', 'transaction_uuid']
    
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'timestamp')

class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'verified', 'otp_code')    






admin.site.register(Product,ProductAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Vendor,VendorAdmin)
admin.site.register(ProductReview,ProductReviewAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(ContactMessage)
admin.site.register(OTP,OTPAdmin)

