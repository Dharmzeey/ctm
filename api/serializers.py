import re
from rest_framework import serializers
from user.models import User, State, Location, Institution, Vendor, VendorApplication, SubscriptionHistory
from store.models import Store, Product, ProductImage, Cart, Sales

# USER, STORE 

# USER RELATED SERIALIZERS
class UserSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, error_messages={
    'required': 'Please enter a password',
    'min_length': 'Password must be at least 8 characters long',
    'max_length': 'Password must be no more than 128 characters long',
    'invalid': 'Please enter a valid password'
  })
  username = serializers.CharField(min_length=4, max_length=150, error_messages={
    'required': 'Please enter a username',
    'min_length': 'Username must be at least 4 characters long',
    'max_length': 'Username must be no more than 150 characters long',
    'invalid': 'Please enter a valid username',
  })
  
  class Meta:
    model = User
    fields = ['username', 'password']
      
  def create(self, validated_data):
    password = validated_data.pop("password")
    user = super().create(validated_data)
    user.set_password(password)
    user.save()
    return user
  
  def validate_username(self, value):
    pattern = r'^[a-zA-Z0-9_]+$'  #Only alphanumeric characters and underscores are allowed
    if not re.match(pattern, value):
      raise serializers.ValidationError("Invalid username. Please use only alphanumeric characters and underscores.")
    return value

class StateSerializer(serializers.ModelSerializer):
  class Meta:
    model = State
    fields = ["name"]
    
class LocationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Location
    fields = ["name", "state"]
    
class InstitutionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Institution
    fields = ["name", "state", "location"]


class VendorApplicationSerializer(serializers.ModelSerializer):
  class Meta:
    model = VendorApplication
    fields = ["applicant"]
    
class VendorSerializer(serializers.ModelSerializer):
  class Meta:
    model = Vendor
    fields = "__all__"
    
class SubscriptionHistorySerializer(serializers.ModelSerializer):
  class Meta:
    model = SubscriptionHistory
    fields = "__all__"
    
    
# STORE RELATED SERIALIZERS
class StoreSerializer(serializers.ModelSerializer):
  class Meta:
    model = Store
    fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = "__all__"
    
class ProductImageSerializer(serializers.ModelSerializer):
  class Meta:
    model = ProductImage
    field = "__all__"

class CartSerializer(serializers.ModelSerializer):
  class Meta:
    model = Cart
    fields = "__all__"
  
class SalesSerializer(serializers.ModelSerializer):
  class Meta:
    model = Sales
    fields = "__all__"