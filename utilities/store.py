from user.models import State, Location, Institution
from store.models import Store

"""
Takes in some params and returns stores and place
"""

def load_stores_helper(state_id=None, location_id=None, institution_id=None):
  if state_id:
    place = State.objects.get(id=state_id)
    stores = Store.objects.filter(owner__active_subscription=True, store_state__id=state_id).order_by("store_name")
    context = {"stores": stores, "place": place}
  elif location_id:
    place = Location.objects.get(id=location_id)
    stores = Store.objects.filter(owner__active_subscription=True, store_location__id=location_id).order_by("store_name")
    context = {"stores": stores, "place": place}
  elif institution_id:
    place = Institution.objects.get(id=institution_id)
    stores = Store.objects.filter(owner__active_subscription=True, store_institution__id=institution_id).order_by("store_name")
    context = {"stores": stores, "place": place}
  return context
