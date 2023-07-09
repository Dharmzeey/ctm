from store.models import Store
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

class SubscriptionCheckMixin:
  def dispatch(self, request, *args, **kwargs):  
    context = {} 
    # THIS FIRST ONE WILL CHECK AND EXECUTE IF THE CURRENT USER IS NOT THE OWNER OF THE STORE
    store_name = kwargs.get("store_name", None)
    if store_name:
      try:
        store = Store.objects.get(store_name__iexact=store_name)
      except:
        return redirect(reverse_lazy('store:list_stores'))        
      if not store.owner.is_subscription_active and not store.owner.active_subscription:
        context.update({"store_name": store, "inactive": True})
      
      
    # THIS FIRST ONE WILL CHECK AND EXECUTE IF THE CURRENT USER IS THE OWNER OF THE STORE
    if (request.user.is_authenticated and request.user.user_info.is_vendor) and (not request.user.selling_vendor.is_subscription_active) and (not request.user.selling_vendor.active_subscription):
      owner = Store.objects.get(owner__seller=request.user.id)
      context.update({"owner": owner, "inactive": True})
    
    # THIS CONTEXT WILL NOT BE EMPTY IF ANY OF THE CONDITION ABOVE IS TRUE AND IT WILL SET INACIVE TO TRUE
    if context:
      return render(request, self.template_name, context)
    return super().dispatch(request, *args, **kwargs)
  
  

    """The above code will first (is_subscription_active) check the @property of the Vendor model in the user app, then if the subscription has expired it will deactivate the store and then it will no longer be accessible
    The (active_subscription) will check the field, more like a confirmation of the @property and the if the store is False, the store will not be assessible
    """
    