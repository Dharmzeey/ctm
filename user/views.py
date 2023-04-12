from datetime import timedelta, datetime, timezone
import pytz
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .forms import ProfileForm, ActivateSubscriptionForm
from .models import User, Vendor, SubscriptionHistory
from store.models import Product

# class ProfileView(View):
#   template_name = "user/profile.html"
#   model = User
#   def get(self, request):
#     profile = get_object_or_404(self.model, id=request.user.id)
#     form = ProfileForm(instance=profile)
#     context = {"form": form}
#     return render(request, self.template_name, context)
  
#   def post(self, request):
#     return 

class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
  template_name = "user/profile.html"
  form_class = ProfileForm
  model = User
  success_url = reverse_lazy("profile_view")
  context_object_name = "profile"
  success_message = "Profile Updated Successfully"
  
  def get_object(self):
    profile = get_object_or_404(self.model, id=self.request.user.id)
    return profile
profile_view = ProfileView.as_view()


class RecentlyViewed(ListView):
  model = Product
  template_name = "user/recently-viewed.html"
  context_object_name = "goods"
  def get_queryset(self):
    recent = self.request.session.get("recently_viewed", None)
    if recent:
      qs = Product.objects.filter(uuid__in=recent)
      return qs
    return Product.objects.none()    
recently_viewed = RecentlyViewed.as_view()

class VendorRequest(LoginRequiredMixin, View):
  template_name = "user/vendor-request.html"
  def get(self, request):
    if request.user.is_vendor:
      # IF THE PERSON IS ALREADY A VENDOR
      messages.info(request, "You are already a vendor")
      store_name = self.request.user.selling_vendor.store_owner.store_name
      return redirect(reverse_lazy("store:detail_store", kwargs={'store_name': store_name}))
    else:
      return render(request, self.template_name)
    
  def post(self, request):
    # ACTIVATES THE IS_VENDOR OF USER
    user = User.objects.get(id=request.user.id)
    user.is_vendor = True
    user.save()
    
    # FREE TRIAL EXPIRES AFTER SEVEN DAYS
    time_now = datetime.now()
    timezone = pytz.timezone('Africa/Lagos')
    naive_expiry_date = time_now + timedelta(days=7)    
    expiry_date = timezone.localize(naive_expiry_date)
    vendor = Vendor.objects.create(
      seller = user,
      active_subscription = True,
      subscription_plan = 2000,
      subscription_duration = 7,
      subscription_expire = expiry_date,
    )
    vendor.save()
    
    messages.success(request, "7 days free trial activated 😊")   
    messages.info(request, "Please Create your store profile")   
    return HttpResponseRedirect(reverse_lazy("store:create_store"))
vendor_request = VendorRequest.as_view()


class VendorView(LoginRequiredMixin, View):
  template_name = "user/vendor.html"
  def get(self, request):
    if request.user.is_vendor:
      vendor = Vendor.objects.get(seller=request.user)
      expiry = vendor.subscription_expire
      timezone = pytz.timezone('Africa/Lagos')
      current_time = timezone.localize(datetime.now())
      days_remaining = expiry - current_time
      try:
        latest_sub = SubscriptionHistory.objects.filter(vendor=vendor)[0]
      except:
        latest_sub = "Free Trial"
      context = {"vendor": vendor, "latest_sub": latest_sub, "days_remaining": days_remaining.days}
    return render(request, self.template_name, context)
vendor_view = VendorView.as_view()


class ActivateSubscription(LoginRequiredMixin, FormView):
  template_name = "user/subscription.html"
  form_class = ActivateSubscriptionForm
  
  def get(self, request):
    # WILL DENY IF VENDOR HAS AN ACTIVE SUBSCRIPTION
    if request.user.selling_vendor.active_subscription:
      messages.info(request, "You have an existing subscription")
      return redirect(reverse_lazy("vendor"))
    return super().get(request)
    
  def form_valid(self, form):
    if form.is_valid():
      package = form.cleaned_data["package"]
      duration = form.cleaned_data["duration"]
      total = int(package) * int(duration)
      
      # THE PAYMENT LOGIC WILL BE HERE and ensure that there is no magomago
      payment_successful = True
      if payment_successful:
        time_now = datetime.now()
        native_expiry_date = time_now + timedelta(days=duration*30)
        timezone = pytz.timezone('Africa/Lagos')
        expiry_date = timezone.localize(native_expiry_date)
        seller_id = self.request.user.id
        
        # THIS WILL GET THE VENDOR AND ACTIVATE THE STORE
        vendor = Vendor.objects.get(seller=seller_id)
        vendor.active_subscription = True
        vendor.subscription_plan = int(package)
        vendor.subscription_duration = int(duration * 30)
        vendor.subscription_expire = expiry_date   
        vendor.save()     

        # THIS WILL UP SUBSCRIPTION HISTORY OF THE VENDOR
        subs_history = SubscriptionHistory.objects.create(
          vendor=vendor,
          amount_paid=total,
          subscription_plan=int(package),
          duration=int(duration * 30), 
          expire_on=expiry_date
        )
        subs_history.save()
        messages.success(self.request, f"Congratulations!!! Your {duration} months plan has successfully been activated")
        # IF FORM VALID AND PAYMENT SUCCESSFUL
        return super(ActivateSubscription, self).form_valid(form)
      # IF PAYMENT NOT SUCCESSFUL BUT FORM VALID
      messages.error(self.request, "Payment Failed!!!")
      return render(self.request, self.template_name, {'form': form})
    # IF FORM NOT VALID
    return render(self.request, self.template_name, {'form': form})
  
  def get_success_url(self):
    store_name = self.request.user.selling_vendor.store_owner
    return reverse_lazy('store:detail_store', kwargs={'store_name': store_name})
activate_subscription = ActivateSubscription.as_view()


class SubscriptionHistoryView(LoginRequiredMixin, View):
  template_name = "user/subscription-history.html"
  model = SubscriptionHistory
  def get(self, request):
    if request.user.is_vendor:
      vendor = Vendor.objects.get(seller=request.user.id)
      history = self.model.objects.filter(vendor=vendor)
      context = {"histories": history}
      return render(request, self.template_name, context)
    else:
      return redirect(reverse_lazy('home'))
subscription_history = SubscriptionHistoryView.as_view()
