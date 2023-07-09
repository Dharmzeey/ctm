from django.urls import path
from . import views

urlpatterns = [
  path("profile-create/", views.profile_create, name="profile_create"),
  path("profile/", views.profile_view, name="profile_view"),
  path("recently-viewed/", views.recently_viewed, name="recently_viewed"),
  
  path("become-a-vendor/", views.vendor_request, name="vendor_request"),
  path("vendor/", views.vendor_view, name="vendor"),
  path("subscribe/", views.activate_subscription, name="activate_subscription"),
  path("subscription-history/", views.subscription_history, name="subscription_history"),
  
]

