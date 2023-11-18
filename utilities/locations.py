from django.http import JsonResponse
from user.models import Location, Institution, State, UserInfo
from store.models import Store
from django.shortcuts import render

'''
THE ARRANGEMENT OF INSTITUTION FIRST AND THE LOCATION AND THEN STATE IS OF THE FACT THAT IF INSTITUTION IS PRESENT,
THAT MEANS THE LOCATION AND STATE IS AVAILABLE BECAUSE INSTITUTION CAN NOT BE SET WITHOUT STATE AND LOCATION 
ALSO, IF LOCATION IS PRESENT, THAT MEAN STATE IS AVAILABLE AND LASTLY STATE
BUT IT IS POSSIBLE FOR THERE TO BE LOCATION WITHOUT INSTITUTION,
SO IF THE INSTIUTION IS EXECUTED THEN IT WILL SKIP LOCATION AND STATE
'''

def set_viewing_location(request):
  try:
    if request.user.is_authenticated:
      request.user.user_info
  except UserInfo.DoesNotExist:
      return None
    # return redirect(reverse_lazy("profile_create"))
  
  if request.user.is_authenticated and (request.user.user_info.institution or request.user.user_info.location or request.user.user_info.state):
    user = request.user
    # checks if it already been set
    viewing_institution = request.session.get("viewing_institution", None)
    viewing_location = request.session.get("viewing_location", None)
    viewing_state = request.session.get("viewing_state", None)
    # THE SESSION WILL GET ASSIGNED IF THEY DO NOT EXIST ELSE IT JUST PASS
    if user.user_info.institution:
      if not viewing_institution and not viewing_location and not viewing_state:
        request.session["viewing_institution"] = str(user.user_info.institution.id)
        request.session["viewing_location"] = str(user.user_info.location.id)
        request.session["viewing_state"] = str(user.user_info.state.id)
        request.session["viewing_institution_name"] = str(user.user_info.institution.name)
        request.session["viewing_location_name"] = str(user.user_info.location.name)
        request.session["viewing_state_name"] = str(user.user_info.state.name)
    elif user.user_info.location:
      if not viewing_location and not viewing_state:
        request.session["viewing_location"] =  str(user.user_info.location.id)
        request.session["viewing_state"] = str(user.user_info.state.id)
        request.session["viewing_location_name"] =  str(user.user_info.location.name)
        request.session["viewing_state_name"] = str(user.user_info.state.name)
    elif user.user_info.state:
      if not viewing_state:
        request.session["viewing_state"] = str(user.user_info.state.id)
        request.session["viewing_state_name"] = str(user.user_info.state.name)
  return 1

# This will trigger when the user is on the web homepage and then changing viewing information
def change_viewing_location(request):
  state_id = request.GET.get('state', None)
  location_id = request.GET.get('location', None)
  institution_id = request.GET.get('institution', None)
  if state_id:
    # SET THE SESSION OF STATE AND THE POPULATE THE FILTER FOR LOCATION MODEL
    state = State.objects.get(id=state_id)
    request.session["viewing_state"] = str(state.id)
    request.session["viewing_state_name"] = str(state.name)
    request.session.pop("viewing_location", None)
    request.session.pop("viewing_institution", None)    
    request.session.pop("viewing_location_name", None)
    request.session.pop("viewing_institution_name", None)    
    locations = Location.objects.filter(state__id=state_id).order_by("name")
    return render(request, 'store/data-list.html', {'locations': locations})
  
  elif location_id:
    location = Location.objects.get(id=location_id)
    request.session["viewing_location"] = str(location.id)
    request.session["viewing_location_name"] = str(location.name)
    request.session.pop("viewing_institution", None)    
    request.session.pop("viewing_institution_name", None)    
    institutions = Institution.objects.filter(location__id=location_id).order_by("name")
    return render(request, 'store/data-list.html', {'institutions': institutions})
  
  elif institution_id:
    institution = Institution.objects.get(id=institution_id)
    request.session["viewing_institution"] = str(institution.id)
    request.session["viewing_institution_name"] = str(institution.name)
    return JsonResponse({"success": "Done"})
  return JsonResponse({"error": "An error occured"})

# This will reset the request.session viweing details
def reset_general(request):
  reset = request.GET.get("reset", None)
  general = request.GET.get("general", None)
  
  if reset:
    request.session.pop("viewing_state", None)
    request.session.pop("viewing_location", None)
    request.session.pop("viewing_institution", None)
    request.session.pop("viewing_state_name", None)
    request.session.pop("viewing_location_name", None)
    request.session.pop("viewing_institution_name", None)
    
  elif general:
    request.session["viewing_institution"] = "General"
    request.session["viewing_location"] = "General"
    request.session["viewing_state"] = "General"  
    request.session["viewing_institution_name"] = "General"
    request.session["viewing_location_name"] = "General"
    request.session["viewing_state_name"] = "General"  
  return JsonResponse({"data": "Success"})


def filter_store(request):
  # This call will set the vieweing details in the session especially for user who has their details filled
  set_viewing_location(request)
  viewing_institution = request.session.get("viewing_institution", None)
  viewing_location = request.session.get("viewing_location", None)
  viewing_state = request.session.get("viewing_state", None)
  viewing_institution_name = request.session.get("viewing_institution_name", None)
  viewing_location_name = request.session.get("viewing_location_name", None)
  viewing_state_name = request.session.get("viewing_state_name", None)

  place = ""
  if viewing_institution == "General" or viewing_location == "General" or viewing_state == "General":
    store = Store.objects.filter(owner__active_subscription=True)
    place = "Nigeria"
  elif viewing_institution:
    store = Store.objects.filter(owner__active_subscription=True, store_state__id=viewing_state, store_location__id=viewing_location, store_institution__id=viewing_institution)
    place = viewing_institution_name
  elif viewing_location:
    store = Store.objects.filter(owner__active_subscription=True, store_state__id=viewing_state, store_location__id=viewing_location)
    place = viewing_location_name
  elif viewing_state:
    store = Store.objects.filter(owner__active_subscription=True, store_state__id=viewing_state)
    place = viewing_state_name
  else:
    store = Store.objects.filter(owner__active_subscription=True)
    place = "Nigeria"
  return {'stores': store, 'place': place}