from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse

from user.models import UserInfo, Vendor

# THIS MIDDLEWARE ENSURES THAT A VENDOR UPDATES STORE DETAILS
class VendorStoreMiddleware(MiddlewareMixin):
  def process_request(self, request):
    # THIS TRY BLOCK CHECKS IF THE USER HAS FILLED THEIR INFO BEFORE PROCEEDING
    try:
      if request.user.is_authenticated:
        UserInfo.objects.get(user=request.user)
    except UserInfo.DoesNotExist:
      return None
    if request.user.is_authenticated and request.user.user_info.is_vendor:
      try:
        # THIS WILL TRY TO GET THE STORE AND IF IT FAILS THAT MEANS NO STORE ASSOCIATED TO THE VENDOR YET
        request.user.selling_vendor.store_owner
      except:
        # THIS WILL CHECK IF THE REQUEST IS AJAX THAT FILTERS LOCATION OF STORE AND THEN EXCLUDE
        if request.path == reverse_lazy('store:load_data'):
          return None
        elif request.path == reverse_lazy('account_login'):
          return None
        elif request.path != reverse_lazy('store:create_store'):
          messages.info(request, "Please Update your store profile")
          return redirect(reverse_lazy("store:create_store"))
    return None

