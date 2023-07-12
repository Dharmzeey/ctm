from datetime import timedelta
import uuid
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from user.models import User, Vendor, State, Location, Institution


class Store(models.Model):
  owner = models.OneToOneField(Vendor, on_delete=models.SET_NULL, related_name="store_owner", null=True)
  store_name = models.CharField(max_length=50, unique=True, validators=[RegexValidator(r'^[a-zA-Z0-9\s]+$', "Store name can only be alphanumeric")])
  store_state = models.ForeignKey(State, on_delete=models.SET_NULL, related_name="store_state", null=True, blank=True)
  store_location = models.ForeignKey(Location, on_delete=models.SET_NULL, related_name="store_location", null=True, blank=True)
  store_institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, related_name="store_institution", null=True, blank=True)
  store_address = models.CharField(max_length=100)
  store_logo = models.ImageField(upload_to='store/logo')
  store_bg_img = models.ImageField(upload_to='store/bg', null=True)
  store_motto = models.CharField(max_length=50)
  whatsapp_number = models.CharField(max_length=11, validators=[RegexValidator(r'^0\d{10}$', 'Mobile number should be 11 digits starting with 0.')])
  instagram = models.URLField(null=True, blank=True)
  tiktok = models.URLField(null=True, blank=True)
  twitter = models.URLField(null=True, blank=True)
  website = models.URLField(null=True, blank=True)
  def __str__(self):
    return self.store_name


class Product(models.Model):
  uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
  vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, related_name="product_vendor", null=True)
  store = models.ForeignKey(Store, on_delete=models.SET_NULL, related_name="product_store", null=True)
  title = models.CharField(max_length=50)
  description = models.TextField()
  thumbnail = models.ImageField(upload_to="products/%Y/%m")
  price = models.DecimalField(max_digits=15, decimal_places=2)
  created_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    ordering = ["-vendor__subscription_plan", "-created_at"]
  def __str__(self):
    return self.title
  

class ProductImage(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_image")
  image = models.ImageField(upload_to="products/%Y/%m")
  class Meta:
    ordering = ["-id"]
  def __str__(self):
    return f"{self.product.vendor}-{self.product}"


class Cart(models.Model):
  owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="cart_owner", null=True)
  product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name="cart_product", null=True)
  quantity = models.IntegerField()
  cleared = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  delete_cart = models.DateField()
  
  @property
  def delete_cart(self):
    seven_days = self.created_at + timedelta(days=7)
    if timezone.now() > seven_days:
      self.delete()
  def __str__(self):
    return self.product


class Sales(models.Model):
  customer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="sales_customer", null=True)
  vendor = models.ForeignKey(Vendor, related_name="sales_vendor", on_delete=models.SET_NULL, null=True)
  title = models.CharField(max_length=50)
  image = models.ImageField(upload_to="cart/%Y/%m")
  quantity = models.IntegerField()
  price = models.DecimalField(max_digits=15, decimal_places=2)
  date_completed = models.DateTimeField(auto_now_add=True)
  def __str__(self):
    return self.customer
  
  class Meta:
    verbose_name_plural = "Sales"
  
  