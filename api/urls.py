from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
  path('changeviewinginfo/', views.change_viweing_info, name="change_viweing_info"), #Async request
  path('onchangeload/', views.on_change_load, name="on_change_load"), #Async request
  path('homepage/', views.homepage, name="homepage"),
  path('homepagesearch/', views.homepage_search, name="homepage_search"),
  path('recentlyviewed/', views.recently_viewed, name="recently_viewed"),
  
  path('user/create/', views.user_create, name="user_create"),
  path('user/login/', views.user_login, name="user_login"),
  path('user/addinfo/', views.user_addinfo, name="user_addinfo"),
  path('user/updateinfo/', views.user_updateinfo, name="user_updateinfo"),
  path('user/vendorrequest/', views.vendor_request, name="vendor_request"),
  path("user/vendorprofile/", views.vendor_profile, name="vendor_profile"),
  path("user/activatesubscription/", views.activate_subscription, name="activate_subscription"),
  path("user/subscriptionhistory/", views.subscription_history, name="subscription_history"),
  
  path('stores/', views.list_stores, name="list_stores"),
  path('filterstoreplaces/', views.filter_store_place, name="filter_store_place"), #Async request
  path('loadfilteredstores/', views.load_filtered_stores, name="load_filtered_stores"), #Async request
  path('searchstores/', views.search_store, name="search_stores"),
  path('createstore/', views.create_store, name="create_store"),
  path('editstore/', views.edit_store, name="edit_store"),
  path('detailstore/', views.detail_store, name="detail_store"),
  
  path('searchproducts/', views.search_product, name="search_product"),
  path('addproduct/', views.add_product, name="add_product"),
  path('detailproduct/', views.detail_product, name="detail_product"),
  path('editproduct/', views.edit_product, name="edit_product"),
  path('deleteproduct/', views.delete_product, name="delete_product"),
  
  path('makepurchase', views.make_purchase, name="make_purchase"),
]

