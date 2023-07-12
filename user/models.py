import uuid
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class State(models.Model):
  name = models.CharField(max_length=20)  
  def __str__(self):
    return self.name
  
  class Meta:
    ordering = ["name"]
  
class Location(models.Model):
  name = models.CharField(max_length=50)
  state = models.ForeignKey(State, on_delete=models.SET_NULL, related_name="location_state", null=True)
  def __str__(self):
    return self.name

class Institution(models.Model):
  name = models.CharField(max_length=100)  
  state = models.ForeignKey(State, on_delete=models.SET_NULL, related_name="institution_state", null=True)
  location = models.ForeignKey(Location, on_delete=models.SET_NULL, related_name="institution_location", null=True)
  def __str__(self):
    return self.name


class User(AbstractUser):
  username = models.CharField(max_length=50, unique=True)
  password = models.CharField(max_length=128)
  email = models.EmailField(unique=True)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)


class UserInfo(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_info")
  first_name = models.CharField(max_length=150, null=False)
  last_name = models.CharField(max_length=150, null=False)
  email = models.EmailField(unique=True)
  state = models.ForeignKey(State, on_delete=models.SET_NULL, related_name="user_state", null=True)
  location = models.ForeignKey(Location, on_delete=models.SET_NULL, related_name="user_location", null=True)
  institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, related_name="user_institution", null=True, blank=True)
  address = models.CharField(max_length=255)
  tel = models.CharField(max_length=11, validators=[RegexValidator(r'^0\d{10}$', 'Mobile number should be 11 digits starting with 0.')])
  is_vendor = models.BooleanField(default=False)
  def __str__(self):
    return self.user.username
  

class Vendor(models.Model):
  PACKAGES =(
    (2000, "SPOTLIGHT"),
    (5000, "HIGHLIGHT"),
    (10000, "FEATURED"),
  )
  seller = models.OneToOneField(User, on_delete=models.SET_NULL, related_name="selling_vendor", null=True)
  active_subscription = models.BooleanField(default=False)
  subscription_plan = models.IntegerField(choices=PACKAGES)
  subscription_duration = models.IntegerField()
  subscription_expire = models.DateTimeField()
  
  # THIS PROPERTY CHECKS IF THE SUBSCRIPTION EXPIRY IS BEHIND, IF YES, IT WILL DEACTIVATE THE SUBSCRIPTION
  @property
  def is_subscription_active(self):
    if self.subscription_expire and self.subscription_expire > timezone.now():
      return True
    else:
      self.active_subscription = False
      self.save()
      return False
  
  def __str__(self):
    return f"{self.seller}"


class SubscriptionHistory(models.Model):
  uuid = models.UUIDField(default=uuid.uuid4, editable=False)
  PACKAGES =(
    (2000, "SPOTLIGHT"),
    (5000, "HIGHLIGHT"),
    (10000, "FEATURED"),
  )
  vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, related_name="vendor_subscription", null=True)
  amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
  subscription_plan = models.IntegerField(choices=PACKAGES)
  duration = models.IntegerField()
  expire_on = models.DateTimeField()
  sub_date = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    verbose_name_plural = "Subscription History"
    ordering = ["-sub_date"]
  def __str__(self):
    return f'{self.vendor} - {self.sub_date}'
