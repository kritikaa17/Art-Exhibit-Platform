from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField



STATUS_CHOICE = (
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)


STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)


RATING = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True,length=10, max_length=20, prefix= "cat",alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default= "Painting")
    image = models.ImageField(upload_to="category", default= "category.jpg")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src= "%s" width="50" height = "50" />' % (self.image.url))

    def __str__(self):
        return self.title

class Artist(models.Model):
    aid = ShortUUIDField(unique=True,length=10, max_length=20, prefix= "artst",alphabet="abcdefgh12345")     
    title = models.CharField(max_length=100, default="Tyong")
    image = models.ImageField(upload_to=user_directory_path, default="artist.jpg")   
    cover_image = models.ImageField(upload_to=user_directory_path, default="artist.jpg") 
    # description =  models.TextField(null=True, blank= True, default= "I am an artist.")
    description =  RichTextUploadingField(null=True, blank= True, default= "I am an artist.")
    address = models.CharField(max_length=100, default= "123 Main Street")
    contact = models.CharField(max_length=100,default="+(977) (1234) 56789")
    chat_resp_time = models.CharField(max_length=100, default="100")
    shipping_on_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  
    date = models.DateTimeField(auto_now_add=True, null= True, blank=True)


    class Meta:
        verbose_name_plural = "Artists"

    def artist_image(self):
        return mark_safe('<img src= "%s" width="50" height = "50" />' % (self.image.url))

    def __str__(self):
        return self.title

class Tags(models.Model):
    pass  

class Product(models.Model):
    pid = ShortUUIDField(unique=True,length=10, max_length=20,alphabet="abcdefgh12345")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category") 
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="artist") 

    title = models.CharField(max_length=100, default= "Starry Night")
    image = models.ImageField(upload_to=user_directory_path, default= "product.jpg")    
    description =  RichTextUploadingField(null=True, blank= True, default="This is art")

    price = models.DecimalField(max_digits=12, decimal_places=2, default= 4900.15)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, default= 5100.24)

    specifications = RichTextUploadingField(null=True, blank= True)
    type = models.CharField(max_length=100, default= "Painting")
    stock_count = models.CharField(max_length=100, default= "10")
    mfd= models.DateTimeField(auto_now_add=False,null=True,blank=True)

    tags = TaggableManager(blank=True) 

    products_status = models.CharField(choices= STATUS, max_length= 10, default="in_review")

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True,length=4, max_length=10,prefix = "sku",alphabet="abcdefgh12345")

    date = models.DateField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe('<img src= "%s" width="50" height = "50" />' % (self.image.url))

    def __str__(self):
        return self.title

    def get_percentage(self):
        new_price = ((self.old_price-self.price)/self.old_price) * 100
        return new_price

class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")     
    product = models.ForeignKey(Product, related_name= "p_images",on_delete=models.SET_NULL, null=True)  
    date = models.DateField(auto_now_add=True)     

    class Meta:
        verbose_name_plural = "Product Images"



########### Cart, Order,OrderItems ############




class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length= 100, null=True,blank=True)
    email = models.CharField(max_length= 100, null=True,blank=True)
    phone = models.CharField(max_length= 100, null=True,blank=True)
    address = models.CharField(max_length= 100, null=True,blank=True)
    city = models.CharField(max_length= 100, null=True,blank=True)
    state = models.CharField(max_length= 100, null=True,blank=True)
    country = models.CharField(max_length= 100, null=True,blank=True)


    price = models.DecimalField(max_digits=12, decimal_places=2, default= "0.00")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default= "0.00")
    coupons = models.ManyToManyField("core.Coupon", blank=True)

    shipping_method = models.CharField(max_length=100, null=True, blank=True)
    tracking_id = models.CharField(max_length=100, null=True, blank=True)
    tracking_website_address = models.CharField(max_length=100, null=True, blank=True)

    paid_status = models.BooleanField(default=False)
    order_date= models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices = STATUS_CHOICE, max_length= 30, default= "processing")
    sku = ShortUUIDField(null=True,blank=True, length=5, prefix="SKU", max_length=20, alphabet="1234567890")
    oid = ShortUUIDField(null=True,blank=True, length=5, max_length=20, alphabet="1234567890")

    stripe_payment_intent = models.CharField(max_length=1000,null=True,blank=True)

    class Meta:
        verbose_name_plural = "Cart Order"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length= 200)
    product_status = models.CharField(max_length= 200)
    item = models.CharField(max_length= 200)
    image = models.CharField(max_length= 200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default= 4900.15)
    total = models.DecimalField(max_digits=12, decimal_places=2, default= 4900.15)

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def category_image(self):
        return mark_safe('<img src= "%s" width="50" height = "50" />' % (self.image.url))    

    def order_img(self):
        return mark_safe('<img src= "/media/%s" width="50" height = "50" />' % (self.image))    
    

############ Product Review, Wishlists, Address ###########

class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True,related_name="reviews")  
    review = models.TextField()
    rating = models. IntegerField(choices=RATING, default = None)
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"


    def __str__(self):
        return self.product.title

    def get_rating(self):
        return self.rating    


class wishlist_model(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)  
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlists"


    def __str__(self):
        return self.product.title


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    address = models.CharField(max_length=100, null= True)
    mobile = models.CharField(max_length=300, null= True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"


class Coupon(models.Model):
    code = models.CharField(max_length=50)
    discount = models.IntegerField(default=1)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

      