import pytz
from datetime import timedelta, datetime, timezone
from django.forms.forms import BaseForm
from django.http.response import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .forms import ProfileForm, ActivateSubscriptionForm
from .models import User, UserInfo,Vendor, SubscriptionHistory
from store.models import Product
from utilities.vendor import create_vendor, has_vendor_profile, view_vendor, activate_vendor_subscription


class ProfileCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
  template_name = "user/profile.html"  
  form_class = ProfileForm
  model = UserInfo
  success_url = reverse_lazy("profile_view")
  context_object_name = "profile"
  success_message = "Profile Created Successfully"
  
  def get(self, request):
    try:
      UserInfo.objects.get(user=request.user)
      return redirect(reverse_lazy("profile_view"))
    except:
      return super().get(request)  
  def form_valid(self, form):
    form.instance.user = self.request.user
    form.instance.email = self.request.user.email
    form.save()
    return super().form_valid(form)
profile_create = ProfileCreate.as_view()
  
class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
  template_name = "user/profile.html"
  form_class = ProfileForm
  model = UserInfo
  success_url = reverse_lazy("profile_view")
  context_object_name = "profile"
  success_message = "Profile Updated Successfully"
  
  def get(self, request):
    try:
      UserInfo.objects.get(user=request.user)
    except UserInfo.DoesNotExist:
      return redirect(reverse_lazy("profile_create"))
    return super().get(request)
  def get_object(self):
    profile = get_object_or_404(self.model, id=self.request.user.user_info.id)
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
    try:
      if request.user.is_authenticated:
        request.user.user_info
    except UserInfo.DoesNotExist:
      messages.info(request, "Please create your profile first")
      return redirect(reverse_lazy("profile_create"))
    if has_vendor_profile(request):
      # IF THE PERSON IS ALREADY A VENDOR
      messages.info(request, "You are already a vendor")
      store_name = self.request.user.selling_vendor.store_owner.store_name
      return redirect(reverse_lazy("store:detail_store", kwargs={'store_name': store_name}))
    else:
      return render(request, self.template_name)
    
  def post(self, request):
    create_vendor(request)
    messages.success(request, "7 days free trial activated 😊")   
    messages.info(request, "Please Create your store profile")   
    return HttpResponseRedirect(reverse_lazy("store:create_store"))
vendor_request = VendorRequest.as_view()


class VendorView(LoginRequiredMixin, View):
  template_name = "user/vendor.html"
  def get(self, request):
    if has_vendor_profile(request):
      context = view_vendor(request)   
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
      if activate_vendor_subscription(self.request, package, duration):
        messages.success(self.request, f"Congratulations!!! Your {duration} months plan has successfully been activated")
        # IF FORM VALID AND PAYMENT SUCCESSFUL
        return super(ActivateSubscription, self).form_valid(form)
      else:
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
    if has_vendor_profile(request):
      vendor = Vendor.objects.get(seller=request.user.id)
      history = self.model.objects.filter(vendor=vendor)
      context = {"histories": history}
      return render(request, self.template_name, context)
    else:
      return redirect(reverse_lazy('home'))
subscription_history = SubscriptionHistoryView.as_view()
