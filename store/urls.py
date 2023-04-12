from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
  path("", views.list_stores, name="list_stores"),
  path("data-ajax/", views.load_data, name="load_data"),
  path("store-ajax/", views.load_stores, name="load_stores"),
  path("search/", views.search_store, name="search_store"),
  
  path("recently-viewed/", views.recently_viewed, name="recently_viewed"),
  
  path("edit/", views.edit_store, name="edit_store"),
  path("create/", views.create_store, name="create_store"),
  path("<str:store_name>/", views.detail_store, name="detail_store"),
  
  path("<str:store_name>/add/", views.add_product, name="add_product"),
  path("<str:store_name>/<str:product_uuid>/", views.detail_product, name="detail_product"),
  path("<str:store_name>/<str:product_uuid>/edit/", views.edit_product, name="edit_product"),
  path("<str:store_name>/<str:product_uuid>/delete/", views.delete_product, name="delete_product"),
  
  path("<str:store_name>/<str:product_uuid>/make-purchase/", views.make_purchase, name="make_purchase"), 
]
