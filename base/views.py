from django.db.models import Q
from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import JsonResponse

from user.models import Location, Institution, State
from store.models import Product, Store
from store.forms import FilterForm

'''
THE ARRANGEMENT OF INSTITUTION FIRST AND THE LOCATION AND THEN STATE IS OF THE FACT THAT IF INSTITUTION IS PRESENT,
THAT MEANS THE LOCATION AND STATE IS AVAILABLE BECAUSE INSTITUTION CAN NOT BE SET WITHOUT STATE AND LOCATION 
ALSO, IF LOCATION IS PRESENT, THAT MEAN STATE IS AVAILABLE AND LASTLY STATE
BUT IT IS POSSIBLE FOR THERE TO BE LOCATION WITHOUT INSTITUTION,
SO IF THE INSTIUTION IS EXECUTED THEN IT WILL SKIP LOCATION AND STATE
'''
def set_viewing_location(request):
  if request.user.is_authenticated and (request.user.institution or request.user.location or request.user.state):
    viewing_institution = request.session.get("viewing_institution", None)
    viewing_location = request.session.get("viewing_location", None)
    viewing_state = request.session.get("viewing_state", None)
    # THE SESSION WILL GET ASSIGNED IF THEY DO NOT EXIST ELSE IT JUST PASS
    if request.user.institution:
      if not viewing_institution and not viewing_location and not viewing_state:
        request.session["viewing_institution"] = str(request.user.institution)
        request.session["viewing_location"] = str(request.user.location)
        request.session["viewing_state"] = str(request.user.state)
    elif request.user.location:
      if not viewing_location and not viewing_state:
        request.session["viewing_location"] =  str(request.user.location)
        request.session["viewing_state"] = str(request.user.state)
    elif request.user.state:
      if not viewing_state:
        request.session["viewing_state"] = str(request.user.state)
  return 1
  
def filter_store(request, model):
  set_viewing_location(request)
  viewing_institution = request.session.get("viewing_institution", None)
  viewing_location = request.session.get("viewing_location", None)
  viewing_state = request.session.get("viewing_state", None)
  
  if viewing_institution == "General" or viewing_location == "General" or viewing_state == "General":
    store = model.objects.all()
  elif viewing_institution:
    store = model.objects.filter(store_state__name=viewing_state, store_location__name=viewing_location, store_institution__name=viewing_institution)
  elif viewing_location:
    store = model.objects.filter(store_state__name=viewing_state, store_location__name=viewing_location)
  elif viewing_state:
    store = model.objects.filter(store_state__name=viewing_state)
  else:
    store = model.objects.all()
  return store

def load_data(request):
  state_id = request.GET.get('state', None)
  location_id = request.GET.get('location', None)
  institution_id = request.GET.get('institution', None)
  if state_id:
    # SET THE SESSION OF STATE AND THE POPULATE THE FILTER FOR LOCATION MODEL
    state = State.objects.get(id=state_id)
    request.session["viewing_state"] = str(state)
    request.session.pop("viewing_location", None)
    request.session.pop("viewing_institution", None)
    
    locations = Location.objects.filter(state__id=state_id).order_by("name")
    return render(request, 'store/data_list.html', {'locations': locations})
  
  if location_id:
    location = Location.objects.get(id=location_id)
    request.session["viewing_location"] = str(location)
    request.session.pop("viewing_institution", None)
    
    institutions = Institution.objects.filter(location__id=location_id).order_by("name")
    return render(request, 'store/data_list.html', {'institutions': institutions})
  
  if institution_id:
    institution = Institution.objects.get(id=institution_id)
    request.session["viewing_institution"] = str(institution)
  return JsonResponse({"error": "AN error Occured"})

def on_filter_load(request):
  stores = filter_store(request, Store)
  randon_products = Product.objects.filter(vendor__active_subscription=True, store__in=stores).order_by("?")[:30]
  products = Product.objects.filter(id__in=randon_products)
  
  recent_products = Product.objects.filter(vendor__active_subscription=True, store__in=stores).order_by("-created_at")[:50]
  recent = Product.objects.filter(id__in=recent_products)
  context = {
    "products": products,
    "recent": recent,
  }
  return render(request, "home/on-filter-load.html", context)

def reset_general(request):
  reset = request.GET.get("reset", None)
  general = request.GET.get("general", None)
  
  if reset:
    request.session.pop("viewing_state", None)
    request.session.pop("viewing_location", None)
    request.session.pop("viewing_institution", None)
    
  elif general:
    request.session["viewing_institution"] = "General"
    request.session["viewing_location"] = "General"
    request.session["viewing_state"] = "General"  
  return JsonResponse({"data": "Success"})

class HomeView(View):
  template_name = "home/index.html"
  def get(self, request):
    form = FilterForm()
    stores = filter_store(request, Store)
        
    randon_products = Product.objects.filter(vendor__active_subscription=True, store__in=stores).order_by("?")[:30]
    products = Product.objects.filter(id__in=randon_products)
    
    recent_products = Product.objects.filter(vendor__active_subscription=True, store__in=stores).order_by("-created_at")[:50]
    recent = Product.objects.filter(id__in=recent_products)

    context = {
      "products": products,
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

