from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken


def get_validate_send_token(request):
  """_summary_
    IF TOKEN EXISTS AND VALID SEND IT BACK ELSE GENERATES NEW ONE


  Args:
      request: request

  Returns:
      _type_: str['token']
  """
  if request.user.is_authenticated:
    # THIS EXTRACT THE TOKEN FROM THE HEADER AND THEN SENDS IT BACK TO THE FRONTEND
    fetched_token = request.META['HTTP_AUTHORIZATION']
    fetched_token = str(fetched_token).split(" ")[1]
    try:
      token = str(JWTAuthentication().get_validated_token(fetched_token))
    except Exception as e:
      e
    if token:
      return token
    else:
      refresh = RefreshToken.for_user(request.user)
      token  = str(refresh.access_token)
      return token
  
