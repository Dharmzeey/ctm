import pytz
from datetime import datetime, timedelta
from user.models import User, Vendor, SubscriptionHistory

def create_vendor(request):
  # ACTIVATES THE IS_VENDOR OF USER
  user = User.objects.get(id=request.user.id)
  user.user_info.is_vendor = True
  user.user_info.save()
  
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
  return True

def has_vendor_profile(request):
  try:
    request.user.user_info.is_vendor
    Vendor.objects.get(seller=request.user)
    return True
  except Vendor.DoesNotExist:
    return False
  
def view_vendor(request):
  vendor = Vendor.objects.get(seller=request.user)
  expiry = vendor.subscription_expire
  timezone = pytz.timezone('Africa/Lagos')
  current_time = timezone.localize(datetime.now())
  days_remaining = expiry - current_time
  try:
    latest_sub = SubscriptionHistory.objects.filter(vendor=vendor)[0]
  except:
    latest_sub = "Free Trial"
  return {"vendor": vendor, "latest_sub": latest_sub, "days_remaining": days_remaining.days}

def activate_vendor_subscription(request, package, duration):
  total = int(package) * int(duration)

  # THE PAYMENT LOGIC WILL BE HERE and ensure that there is no magomago
  payment_successful = True
  if payment_successful:
    time_now = datetime.now()
    native_expiry_date = time_now + timedelta(days=duration*30)
    timezone = pytz.timezone('Africa/Lagos')
    expiry_date = timezone.localize(native_expiry_date)
    seller_id = request.user.id
    
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
    return True
  return False