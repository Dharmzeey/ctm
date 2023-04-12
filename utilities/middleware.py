from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse

class VendorStoreMiddleware(MiddlewareMixin):
  def process_request(self, request):
    if request.user.is_authenticated and request.user.is_vendor:
      try:
        # THIS WILL TRY TO GET THE STORE AND IF IT FAILS THAT MEANS NO STORE ASSOCIATED TO THE VENDOR YET
        store = request.user.selling_vendor.store_owner
      except:
        # THIS WILL CHECK IF THE REQUEST IS AJAX THAT FILTERS LOCATION OF STORE
        if request.path == reverse_lazy('store:load_data'):
          return None
        elif request.path != reverse('store:create_store'):
          messages.info(request, "Please Update your store profile")
          return redirect(reverse_lazy("store:create_store"))
    return None
        