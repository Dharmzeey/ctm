from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import generics
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from base.views import set_viewing_location, filter_store
from store.models import Product, Store, ProductImage
from user.models import SubscriptionHistory, User, UserInfo, Vendor, Institution
from utilities.vendor import create_vendor, has_vendor_profile, view_vendor, activate_vendor_subscription

from .utilities.error_handler import render_errors
from .utilities.token_handler import get_validate_send_token
from .utilities.user_details import return_user_details
from . import serializers as customAPISerializers

"""
THE USER API VIEWS COMMENCES HERE
"""

class UserCreate(APIView):
  serializer_class = customAPISerializers.UserSerializer
  @extend_schema(
    responses={
      status.HTTP_201_CREATED: OpenApiResponse(
        response=serializer_class,
        examples=[
          OpenApiExample(
            'Login Success',
            value={
              "message": "user created successfully",
              "token": "eyJhbG9.eyJ0b2tlbl90YjVmNTFiIiwidXNlcl9pZCI0.mCGI47XbwaAz_Cqv_UQpWhZs"
            }
          )
        ]
      ),
      status.HTTP_400_BAD_REQUEST: OpenApiResponse(
        response=serializer_class,
        examples=[
          OpenApiExample(
            'User Creation Failed',
            value={
              "message": "User Creation Failed",
            }
          )
        ]
      ),
      status.HTTP_409_CONFLICT: OpenApiResponse(
        response=serializer_class,
        examples=[
          OpenApiExample(
            'User Exists',
            value={
              "message": "User with this email or username already exists",
            }
          )
        ]
      ),
    }
  )
  def post(self, request):
    serializer = self.serializer_class(data=request.data)
    if serializer.is_valid():
      try:
        user = serializer.save()
        tokens = TokenObtainPairSerializer().validate(request.data)
        access_token = tokens['access']
        refresh_token = tokens['refresh']
        data = {
          'message': 'User created successfully',
          'token': access_token,
          # 'refresh_token': refresh_token,
        }
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return Response(data, status=status.HTTP_201_CREATED)
      except IntegrityError:
        return Response({'message': 'User with this email or username already exists.'}, status=status.HTTP_409_CONFLICT)
    return Response({'message': f'User Creation Failed {serializer.errors}'}, status=status.HTTP_400_BAD_REQUEST)
user_create = UserCreate.as_view()


class UserLogin(APIView):
  serializer_class = customAPISerializers.UserSerializer
  @extend_schema(
    responses={
      status.HTTP_200_OK: OpenApiResponse(
      response=serializer_class,
      examples=[
        OpenApiExample(
          'Extra Information',
          value={
          "message": "Login Successful",
          "data": serializer_class().data,
          'token': "eyJhbG9.eyJ0b2tlbl90YjVmNTFiIiwidXNlcl9pZCI0.mCGI47XbwaAz_Cqv_UQpWhZs"
        },
      )
      ]
      ),
      status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
        response=serializer_class,
        examples=[ 
          OpenApiExample(
            'Unauthorized', 
            value={"message": "Invalid Credentials"}
          ),
        ]
      ),
      status.HTTP_404_NOT_FOUND: OpenApiResponse(
        response=serializer_class,
        examples=[ 
          OpenApiExample(
            'User Not Found', 
            value={"message": "User not found"}
          ),
        ]
      ),
    }
  )
  def post(self, request):
    username = request.data.get("username")
    password = request.data.get("password")
    try:
      user = User.objects.get(username=username)
    except User.DoesNotExist:
      return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      refresh = RefreshToken.for_user(user)
      access_token = str(refresh.access_token)
      # ------Checks if the user has added their info------#
      try:
        UserInfo.objects.get(user=user)
      except UserInfo.DoesNotExist:
        data = {"message": "Login successful", "token": access_token}
        return Response(data, status=status.HTTP_200_OK)
      # CALLS THE FUNCTION THAT PROCESSES AND RETURNS USER DATA
      user_details = return_user_details(user, request)            
      data = {"message": "Login successful", "data": user_details, "token": access_token}
      return Response(data, status=status.HTTP_200_OK)
    return Response({"message": "Invalid Credentials",}, status=status.HTTP_401_UNAUTHORIZED)
user_login = UserLogin.as_view()


class UserAddInfo(APIView):
  serializer_class = customAPISerializers.UserInfoSerializer
  permission_classes = [IsAuthenticated]
  
  def post(self, request):
    serializer = self.serializer_class(data=request.data)
    token = get_validate_send_token(request)
    if serializer.is_valid():
      serializer.save(user=request.user, email=request.user.email)
      data = {"message": "Profile created successfully", "data": serializer.data, "token": token}
      return Response(data, status=status.HTTP_201_CREATED)
    data = {"message": render_errors(serializer.errors), "token": token}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
user_addinfo = UserAddInfo.as_view()


class UserUpdateInfo(APIView):
  serializer_class = customAPISerializers.UserInfoSerializer
  permission_classes = [IsAuthenticated]
  
  def patch(self, request):
    user = request.user.user_info
    serializer = self.serializer_class(instance=user, data=request.data, partial=True, context={'request': request})
    token = get_validate_send_token(request)
    if serializer.is_valid():
      serializer.save()
      data = {"message": "Profile updated successfully", "data": serializer.data, "token": token}
      return Response(data, status=status.HTTP_200_OK)
    data = {"message": render_errors(serializer.errors), "token": token}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
user_updateinfo = UserUpdateInfo.as_view()


class RecentlyViewed(generics.ListAPIView):
  model = Product
  serializer_class = customAPISerializers.ProductSerializer
  
  def get_queryset(self):
    # TAKES IN THE UUID OF THE RECENTLY VIEWED PRODUCTS AS A LIST, WHICH IS SENT FROM THE FRONTEND
    recent = self.request.data["recently_viewed"]
    if recent:
      qs = Product.objects.filter(uuid__in=recent)
      return qs
    return Product.objects.none()  
recently_viewed = RecentlyViewed.as_view()


class VendorRequest(APIView):
  permission_classes = [IsAuthenticated]
  def post(self, request):
    token = get_validate_send_token(request)
    try:
      UserInfo.objects.get(user=request.user)
    except UserInfo.DoesNotExist:
      return Response({"message": "Please Create Your Profile first", "token": token}, status=status.HTTP_403_FORBIDDEN)      
    try:
      Vendor.objects.get(seller=request.user)
      return Response({"message": "You are already a vendor", "token": token}, status=status.HTTP_409_CONFLICT)
    except Vendor.DoesNotExist:
      create_vendor(request)
      return Response({"message": "Vendor Profile activated", "token": token}, status=status.HTTP_201_CREATED)
    # FROM HERE IT REDIRECTS TO CREATE STORE PAGE
vendor_request = VendorRequest.as_view()


class VendorProfile(APIView):
  serializer_class = customAPISerializers.VendorSerializer
  permission_classes = [IsAuthenticated]
  def get(self, request):
    if has_vendor_profile(request):
      serializer = self.serializer_class(instance=request.user.selling_vendor)
      vendor = view_vendor(request)
      print(vendor["latest_sub"])
      sub_history = customAPISerializers.SubscriptionHistorySerializer(instance=vendor["latest_sub"]).data
      data = {"data": serializer.data, "token":get_validate_send_token(request), "activated_on": sub_history['sub_date'], "days_remaining": vendor["days_remaining"]}
      return Response(data, status=status.HTTP_200_OK)
    return Response({"message": "You are not a vendor"}, status=status.HTTP_401_UNAUTHORIZED)
vendor_profile = VendorProfile.as_view()


class ActivateSubscription(APIView):
  serializer_class = customAPISerializers.ActivateSubscriptionSerializer
  permission_classes = [IsAuthenticated]
  def post(self, request):
    if request.user.selling_vendor.active_subscription:
      return Response({"message": "You have an existing subscription!!!", "token": get_validate_send_token(request)}, status=status.HTTP_403_FORBIDDEN)
    serializer = self.serializer_class(data=request.data)
    if serializer.is_valid():
      package = serializer.data["package"]
      duration = serializer.data["duration"]
      if activate_vendor_subscription(request, package, duration):
        return Response({"message": f"Congratulations!!! Your {duration} months {package} plan has successfully been activated",  "token": get_validate_send_token(request)}, status=status.HTTP_200_OK)
      return Response({"message": "Payment Failed!!!",  "token": get_validate_send_token(request)}, status=status.HTTP_402_PAYMENT_REQUIRED)
    return Response({"message": "Invalid parameter passed",  "token": get_validate_send_token(request)}, status=status.HTTP_400_BAD_REQUEST)
activate_subscription = ActivateSubscription.as_view()


class SubscriptionHistory(APIView):
  serializer_class = customAPISerializers.SubscriptionHistorySerializer
  model = SubscriptionHistory
  permission_classes = [IsAuthenticated]
  def get(self, request):
    if has_vendor_profile(request):
      vendor = Vendor.objects.get(seller=request.user.id)
      history = self.model.objects.filter(vendor=vendor)
      serializer = self.serializer_class(instance=history, many=True)
      data = {"data": serializer.data, "token": get_validate_send_token(request)}
      return Response(data, status=status.HTTP_200_OK)
subscription_history = SubscriptionHistory.as_view()


"""
store api view commences here
"""

class ListStore(generics.ListAPIView):
  serializer_class = customAPISerializers.StoreSerializer
  queryset = Store.objects.filter(owner__active_subscription=True).order_by("?")
list_stores = ListStore.as_view()


class SearchStore(generics.ListAPIView):
  serializer_class = customAPISerializers.StoreSerializer
  def get_queryset(self):
    q = self.request.data["q"]
    if q:
      return Store.objects.filter(
      Q(store_name__icontains=q),
      owner__active_subscription=True, 
      )
    return super().get_queryset()
search_store = SearchStore.as_view()


class CreateStore(APIView):
  permission_class = [IsAuthenticated]
  parser_classes = [FormParser, MultiPartParser]
  serializer_class = customAPISerializers.StoreSerializer
  def get(self, request):
    institution = Institution.objects.all()
    serializer = customAPISerializers.InstitutionSerializer(instance=institution, many=True)
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)
  
  def post(self, request):
    try:
      Vendor.objects.get(seller=request.user)
    except Vendor.DoesNotExist:
      return Response({"message": "You are not a vendor", "token": get_validate_send_token(request)}, status=status.HTTP_403_FORBIDDEN)
    try:
      Store.objects.get(owner=request.user.selling_vendor)
      data = {"message": "Store for this user exitst already", "token": get_validate_send_token(request)}
      return Response(data, status=status.HTTP_409_CONFLICT)
    except Store.DoesNotExist:
      serializer = self.serializer_class(data=request.data, context={'request': request})
      if serializer.is_valid():
        vendor = request.user.selling_vendor
        serializer.save(owner=vendor)
        data = {"data": serializer.data, "message": "Store Information Created", "token": get_validate_send_token(request)}
        return Response(data, status=status.HTTP_201_CREATED)
      return Response({"message": str(serializer.errors), 'token': get_validate_send_token(request)}, status=status.HTTP_400_BAD_REQUEST)
create_store = CreateStore.as_view()


class EditStore(APIView):
  permission_classes = [IsAuthenticated]
  serializer_class = customAPISerializers.StoreSerializer
  def patch(self, request):
    token = get_validate_send_token(request)
    store = get_object_or_404(Store, owner=self.request.user.selling_vendor.id)
    serializer = self.serializer_class(instance=store, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
      data = {"message": "Profile updated successfully", "data": serializer.data, "token": token}
      return Response(data, status=status.HTTP_200_OK)
    data = {"message": render_errors(serializer.errors), "token": token}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
edit_store = EditStore.as_view()


class StoreDetails(APIView):
  permission_classes = [IsAuthenticatedOrReadOnly]
  def get(self, request):
    store_name = request.data["store_name"]
    try:
      store = Store.objects.get(store_name__iexact=store_name)
    except Store.DoesNotExist:
      return Response({"message": "No store found"}, status=status.HTTP_404_NOT_FOUND)
    if store.owner.active_subscription == False:
      return Response({"message": "Store not active"}, status=status.HTTP_404_NOT_FOUND)
    products = Product.objects.filter(store=store.id)
    store_serializer = customAPISerializers.StoreSerializer(instance=store, context={'request': request})
    product_serializer = customAPISerializers.ProductSerializer(instance=products, many=True, context={'request': request})
    if request.user.is_authenticated and request.user.user_info.is_vendor and (store.owner.seller == request.user):
      owner = Store.objects.get(owner__seller=request.user.id, store_name__iexact=store_name)
      data = {
        "owner": True,
        "store": store_serializer.data,
        "products": product_serializer.data,
      }
    else:
      data = {  
        "store": store_serializer.data,
        "products": product_serializer.data,
      }  
    return Response(data, status=status.HTTP_200_OK)
detail_store = StoreDetails.as_view()


"""
product api view commences here
"""

class SearchProduct(generics.ListAPIView):
  serializer_class = customAPISerializers.ProductSerializer
  def get_queryset(self):
    stores = filter_store(self.request, Store)
    q = self.request.data["q"]
    if q:
      return Product.objects.fiilter(
        Q(title__icontains=q)|
        Q(description__icontains=q),
        vendor__active_subscription=True,
        store__in=stores
      )
    return super().get_queryset()
  
search_product = SearchProduct.as_view()

class AddProduct(generics.CreateAPIView):
  parser_classes = (MultiPartParser,)
  permission_classes = [IsAuthenticated]
  serializer_class = customAPISerializers.ProductSerializer
  
  def create(self, request, *args, **kwargs):
    images = request.FILES.getlist('uploaded_images')
    max_image = int(request.user.selling_vendor.subscription_plan) // 1000
    if len(images) >max_image:
      return Response({"message": f"maximum of {max_image} images allowed"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)
    data = {"message": "Product added successfully", "data": serializer.data, "token": get_validate_send_token(request)}
    return Response(data, status=status.HTTP_201_CREATED, headers=headers)
  
  def perform_create(self, serializer):
    vendor = self.request.user.selling_vendor
    store = vendor.store_owner
    serializer.save(vendor=vendor, store=store)
add_product = AddProduct.as_view()


class ProductDetails(generics.RetrieveAPIView):
  serializer_class = customAPISerializers.ProductSerializer
  def get_object(self):
    store = get_object_or_404(Store, store_name__iexact=self.request.data['store_name'])
    product = get_object_or_404(Product, uuid=self.request.data['product_uuid'], store=store)
    return product
detail_product = ProductDetails.as_view()


class EditProduct(generics.UpdateAPIView):
  permission_classes = [IsAuthenticated]
  serializer_class = customAPISerializers.ProductSerializer
  parser_classes = (MultiPartParser,)
  
  def get_object(self):
    store = self.request.user.selling_vendor.store_owner
    product = get_object_or_404(Product, uuid=self.request.data['product_uuid'], store=store)
    return product
  
  def update(self, request, *args, **kwargs):
    update_response = super().update(request, *args, **kwargs)
    data = {"message": "Product updated", "data": update_response.data, "token": get_validate_send_token(request)}
    return Response(data)
edit_product = EditProduct.as_view()


class DeleteProduct(generics.DestroyAPIView):
  serializer_class = customAPISerializers.ProductSerializer
  permission_classes = [IsAuthenticated]
  def get_object(self):
    store = self.request.user.selling_vendor.store_owner
    product = get_object_or_404(Product, uuid=self.request.data['product_uuid'], store=store)
    return product
  
  def destroy(self, request, *args, **kwargs):
    instance = self.get_object()
    self.perform_destroy(instance)
    return Response({"message": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)
delete_product = DeleteProduct.as_view()


"""
other api code
"""
# Make purchase
class MakePurchase(APIView):
  def get(self, request):
    product_uuid = request.data["product_uuid"]
    store_name = request.data["store_name"]
make_purchase = MakePurchase.as_view()
