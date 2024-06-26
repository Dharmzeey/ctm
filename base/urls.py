from django.urls import path
from . import views

urlpatterns = [
  path("", views.home, name="home"),
  path("search/", views.search, name="search"),
  path("ajax-data", views.load_data, name="load_data"), #Async
  path("filter-load", views.on_filter_load, name="filter_load"), #Async
  path("reset-general", views.reset_general, name="reset_general"), #Async
]