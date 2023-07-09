import re
from rest_framework import serializers
from user.models import User, UserInfo, State, Location, Institution, Vendor, SubscriptionHistory
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
    fields = ['username', 'password', 'email']
      
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
  
class UserInfoSerializer(serializers.ModelSerializer):
  # email = serializers.SerializerMethodField(readonly=True)
  class Meta:
    model = UserInfo
    fields = ["first_name", "last_name", "email", "state", "location", "institution", "address", "tel"]
    read_only_fields = ["email"]

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
    fields = ["id", "name", "state", "location"]
    depth = 1


class VendorSerializer(serializers.ModelSerializer):
  class Meta:
    model = Vendor
    fields = "__all__"
    
class ActivateSubscriptionSerializer(serializers.Serializer):
  PACKAGES =(
    (2000, "SPOTLIGHT"),
    (5000, "HIGHLIGHT"),
    (10000, "FEATURED"),
  )
  package = serializers.ChoiceField(choices=PACKAGES)
  duration = serializers.IntegerField()

class SubscriptionHistorySerializer(serializers.ModelSerializer):
  class Meta:
    model = SubscriptionHistory
    fields = "__all__"
    
    
# store and product related
class StoreSerializer(serializers.ModelSerializer):
  class Meta:
    model = Store
    fields = "__all__"
    read_only_field = ["owner"]
    
class ProductImageSerializer(serializers.ModelSerializer):
  class Meta:
    model = ProductImage
    fields = "__all__"
    
class ProductSerializer(serializers.ModelSerializer) :
  product_image = ProductImageSerializer(many=True, read_only = True)
  uploaded_images = serializers.ListField(
    child = serializers.ImageField(max_length = 1000000, allow_empty_file = False, use_url = False),
    write_only = True
    )
  
  class Meta:
    model = Product
    fields = ["uuid", "vendor", "store", "title", "description", "thumbnail", "price", "product_image", "uploaded_images"]
    read_only_field = ["uuid", "vendor", "store"]

  def create(self, validated_data):
    uploaded_data = validated_data.pop('uploaded_images')
    new_product = Product.objects.create(**validated_data)
    for uploaded_item in uploaded_data:
      ProductImage.objects.create(product = new_product, image = uploaded_item)
    return new_product
  
  def clear_existing_images(self, instance):
    for image in instance.product_image.all():
      image.delete()
  
  def update(self, instance, validated_data):
    uploaded_data = validated_data.pop('uploaded_images', None)
    if uploaded_data:
      self.clear_existing_images(instance) # This clears the existing images
      for uploaded_item in uploaded_data:
        ProductImage.objects.create(product = instance, image = uploaded_item)
    return super().update(instance, validated_data)

class CartSerializer(serializers.ModelSerializer):
  class Meta:
    model = Cart
    fields = "__all__"
  
class SalesSerializer(serializers.ModelSerializer):
  class Meta:
    model = Sales
    fields = "__all__"