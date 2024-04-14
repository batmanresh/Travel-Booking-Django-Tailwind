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
    cid=ShortUUIDField(unique=True, length=10, max_length=20,prefix="cat",alphabet="abcdefgh12345",default="NO Category")
    title=models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural="Categories"

    def __str__(self):
        return self.title 

# class Tags(models.Model):
#     pass

class Vendor(models.Model):

    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100,default="Title Error")
    image = models.ImageField(upload_to=user_directory_path,default=None,blank=True)
    description = models.TextField(null=True, blank=True,default="No Description")
    address = models.CharField(max_length=106, default="123 Main Street.")
    contact = models.CharField(max_length=100, default="+123 (456) 789")
    experience = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")

    user=models.ForeignKey(User, on_delete=models.SET_NULL,null=True)

    class Meta:
        verbose_name_plural="Vendors"

    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' %(self.image.url))

    def __str__(self):
        return self.title 
    
class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100,default="Title Error")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = models.TextField(null=True, blank=True,default="Contact vendor for more information.")

    user=models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    category=models.ForeignKey(Category, on_delete=models.SET_NULL,null=True)

    price=models.DecimalField(max_digits=8,decimal_places=2,default="1.00")
    old_price=models.DecimalField(max_digits=8,decimal_places=2,default="5.00")

    specifications = models.TextField(null=True, blank=True)
    # tags=models.ForeignKey(Tags, on_delete=models.SET_NULL,null=True)

    product_status=models.CharField(choices=STATUS,max_length=10,default="in_review")
    status=models.BooleanField(default=True) 
    featured=models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix="sku", alphabet="abcdefgh12345")
    startDate=models.DateTimeField(null=True,blank=True)
    updated=models.DateTimeField(null=True,blank=True)



    class Meta:
        verbose_name_plural="Products"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' %(self.image.url))

    def __str__(self):
        return self.title 
    
    def get_percentage(self):
        new_price=(self.price/self.old_price)*100
        return new_price
    
class ProductImages(models.Model):
    images=models.ImageField(upload_to="product-images",default="product.jpg")
    product=models.ForeignKey(Product,related_name="p_images", on_delete=models.SET_NULL,null=True)
    date=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="Product Images"


####################### product review, wishlist ################################
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
    








# HOTEL_STATUS={
#     ("Draft","Draft"),
#     ("Disabled","Disabled"),
#     ("Rejected","Rejected"),
#     ("In Review","In Review"),
#     ("Live","Live"),
# }

# class destination(models.Model):
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     name = models.CharField(max_length=100)
#     description = models.TextField(null=True, blank=True)
#     image = models.FileField(upload_to="destination_gallery")
#     address = models.CharField(max_length=200)
#     mobile = models.CharField(max_length=200)
#     email = models.EmailField(max_length=100)
    
#     status = models.CharField(max_length=20, choices=HOTEL_STATUS, default="Live")
    
#     tags = models.CharField(max_length=200, help_text="Separate tags with comma")
#     views = models.IntegerField(default=0)
#     featured = models.BooleanField(default=False)

    
    
#     hid = ShortUUIDField(unique=True, max_length=28)
#     slug = models.SlugField(unique=True)
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name

#     def save(self, *args, **kwargs):
#         if not self.slug or not self.hid:
#             uniqueid = shortuuid.uuid()[:4]
#             self.slug = slugify(self.name + "-" + str(uniqueid).lower())
#             self.hid = uniqueid
        
#         super(destination, self).save(*args, **kwargs)

#     def thumbnail(self):
#         return mark_safe("<img src='%s' width='50' height='50' style='object-fit: cover; border-radius: 6px;' />" % (self.image.url))

# class destination_preview(models.Model):

#     id = models.IntegerField(primary_key=True)
#     country = models.CharField(max_length=20)
#     img1 = models.ImageField(upload_to='pics')
#     img2 = models.ImageField(upload_to='pics')
#     number = models.IntegerField(default=2)

#     class Meta:
#         app_label = 'Travel'

# class Detailed_desc(models.Model):
#     dest_id = models.AutoField(primary_key=True)
#     country = models.CharField(max_length=20)
#     days = models.IntegerField(default=5)
#     price = models.IntegerField(default=20000)
#     rating = models.IntegerField(default=5)
#     dest_name = models.CharField(max_length=25)
#     img1=models.ImageField(upload_to='pics')
#     img2 = models.ImageField(upload_to='pics')
#     desc = models.TextField()
#     day1= models.CharField(max_length=200)
#     day2 = models.CharField(max_length=200)
#     day3 = models.CharField(max_length=200)
#     day4 = models.CharField(max_length=200)
#     day5 = models.CharField(max_length=200)
#     day6 = models.CharField(max_length=200)
