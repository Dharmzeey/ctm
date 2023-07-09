from api.serializers import UserInfoSerializer
from user.models import User

def return_user_details(user, request):
  """
  Gets user details and returns
  _summary_

  Args:
      user (_type_): _description_
      request (_type_): _description_

  Returns:
      _type_: _description_
  """
  current_user = User.objects.get(username=user.username)
  user_info_serializer = UserInfoSerializer(instance=current_user.user_info, context = {'request': request}).data
  return user_info_serializer
