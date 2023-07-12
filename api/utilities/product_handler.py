from rest_framework import status
from rest_framework.response import Response

from base.views import filter_store
from store.models import Store, Product
from user.models import State
from api import serializers

# Displays the products based on viewing details
def show_product_helper(request):
  stores = filter_store(request, Store)
  random_products = Product.objects.filter(vendor__active_subscription=True, store__in=stores).order_by("?")[:5]
  random = Product.objects.filter(id__in=random_products) # This line is to use the model ordering whieh is by (vendor subscription plan first and then -created at)
  random_product_serializer = serializers.ProductSerializer(instance=random, many=True, context={"request": request})
  
  recent_products = Product.objects.filter(vendor__active_subscription=True, store__in=stores).order_by("-created_at")[:5]
  recent = Product.objects.filter(id__in=recent_products) # This line is to use the model ordering whieh is by (vendor subscription plan first and then -created at)
  recent_product_serializer = serializers.ProductSerializer(instance=recent, many=True, context={"request": request})
  states = State.objects.all()
  state_serializer = serializers.StateSerializer(instance=states, many=True)
  data = {
    "random_products": random_product_serializer.data,
    "recent_products": recent_product_serializer.data,
    "states": state_serializer.data
  }
  return Response(data, status=status.HTTP_200_OK)
