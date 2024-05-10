from django.db import models
from django import forms
from django.template.defaultfilters import slugify
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField
import shortuuid




STATUS_CHOICE={
    ("process","Processing"),
    ("confirmed","Confirmed"),
}

STATUS={
    ("draft","Draft"),
    ("disabled","Disabled"),
    ("rejected","Rejected"),
    ("in_review","In Review"),
    ("published","Published")
}

RATING={
    (1,"★☆☆☆☆"),
    (2,"★★☆☆☆"),
    (3,"★★★☆☆"),
    (4,"★★★★☆"),
    (5,"★★★★★"),
}

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id,filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdefgh12345", default="NO Category")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True) 

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title
    


class Vendor(models.Model):

    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100,default="Title Error")

    description = models.TextField(null=True, blank=True,default="No Description")
    address = models.CharField(max_length=106, default="123 Main Street.")
    contact = models.CharField(max_length=100, default="+123 (456) 789")
    experience = models.CharField(max_length=100, default="100")

    user=models.ForeignKey(User, on_delete=models.SET_NULL,null=True)

    class Meta:
        verbose_name_plural="Vendors"

    

    def __str__(self):
        return self.title 
    
class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20,prefix="ven", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Title Error")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = models.TextField(null=True, blank=True, default="Contact vendor for more information.")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    price = models.IntegerField(default=1)
    old_price = models.IntegerField(default=2)

    specifications = models.TextField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
     
    product_status = models.CharField(
        choices=STATUS, max_length=10, default="in_review")
    status = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    sku = models.IntegerField(default=0)


    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

    def get_percentage(self):
        if self.old_price != 0:
            discount_percentage = 100 - ((self.price / self.old_price) * 100)
            return discount_percentage
        else:
            return 0
    def decrease_sku(self, num_guests):
        """
        Decreases the SKU by the specified number of guests.
        """
        if self.sku >= num_guests:
            self.sku -= num_guests
            self.save()
            return True
        else:
            return False



class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    verified = models.BooleanField(default=False)
    def __str__(self):
        return self.otp_code


    
class ProductImages(models.Model):
    images=models.ImageField(upload_to="product-images",default="product.jpg")
    product=models.ForeignKey(Product,related_name="p_images", on_delete=models.SET_NULL,null=True)
    date=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="Product Images"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


####################### product review ################################
class ProductReview(models.Model):
    user=models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    product=models.ForeignKey(Product, on_delete=models.SET_NULL,null=True)
    review=models.TextField()
    rating=models.IntegerField(choices=RATING, default=None)
    date=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural="Product Reviews"


    def __str__(self):
        return self.product.title 
    
    def get_rating(self):
        return self.rating
    


from django.db import models

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    num_guests = models.IntegerField()
    special_requests = models.TextField(default='')  
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_uuid = models.CharField(max_length=255, unique=True)
    transaction_code = models.CharField(
        max_length=255, null=True, blank=True)  
    transaction_status = models.CharField(
        max_length=50, null=True, blank=True)  

    def __str__(self):
        return f"{self.user.username}'s Booking for {self.product.title}"




class TemporaryFormSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
    travel_date = models.DateField()
    interests = models.TextField()

    def __str__(self):
        return f"Temporary Form Submission - {self.user.username}"

