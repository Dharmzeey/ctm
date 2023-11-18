from django.db.models import Q
from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView

from utilities.locations import set_viewing_location, change_viewing_location, reset_general, filter_store
from store.models import Product, Store
from store.forms import FilterForm


def load_data(request):
  return change_viewing_location(request)

# This will trigger when the user is on the homepage and then changing viewing information, the products are then filtered and displayed
def on_filter_load(request):
  # This checks for the session viewing information set by the previous function
  stores = filter_store(request)['stores']
  print(filter_store(request))
  random_products = Product.objects.filter(vendor__active_subscription=True, store__in=stores).order_by("?")[:30]
  products = Product.objects.filter(id__in=random_products) 
  
  recent_products = Product.objects.filter(vendor__active_subscription=True, store__in=stores).order_by("-created_at")[:50]
  recent = Product.objects.filter(id__in=recent_products)
  context = {
    "products": products,
    "recent": recent,
  }
  return render(request, "home/on-filter-load.html", context)

class HomeView(View):
  template_name = "home/index.html"
  def get(self, request):
    form = FilterForm(request=request)
    stores = filter_store(request)['stores']
        
    random_products = Product.objects.filter(vendor__active_subscription=True, store__in=stores).order_by("?")[:30]
    random = Product.objects.filter(id__in=random_products) # This line is to use the model ordering whieh is by (vendor subscription plan first and then -created at)
    
    recent_products = Product.objects.filter(vendor__active_subscription=True, store__in=stores).order_by("-created_at")[:50]
    recent = Product.objects.filter(id__in=recent_products) # This line is to use the model ordering whieh is by (vendor subscription plan first and then -created at)

    context = {
      "products": random,
      "recent": recent,
      "form": form,
      "home": True
    }
    return render(request, self.template_name, context)
home = HomeView.as_view()


class HomeSearch(ListView):
  model = Product
  context_object_name = "goods"
  template_name = "home/search-result.html"
  
  def get_queryset(self):
    stores = filter_store(self.request, Store)    
    q = self.request.GET.get("q", None)
    if q:
      return super().get_queryset().filter(
        Q(title__icontains=q)|
        Q(description__icontains=q),
        vendor__active_subscription=True,
        store__in=stores
      )
    return super().get_queryset()
  
  # def get_context_data(self, **kwargs):
  #   form = FilterForm()
  #   context =  super().get_context_data(**kwargs)
  #   context["form"] = form
  #   return context
search = HomeSearch.as_view()


