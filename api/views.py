from rest_framework.views import APIView
from .serializers import (UserSerializer)

class UserCreate(APIView):
  serializer_class = UserSerializer