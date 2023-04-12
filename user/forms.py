from django import forms
from .models import User, Institution, Location

class ProfileForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ["first_name", "last_name", "email", "state", "location", "institution", "address", "tel"]
    widgets = {
      "email" : forms.TextInput(attrs={'readonly':'readonly'})
    }
    
    labels = {
      'email': "Email Address",
      'tel': "Phone Number"
    }
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields["location"].queryset = Location.objects.none()
    self.fields["institution"].queryset = Institution.objects.none()
    
    if 'state' in self.data and 'location' in self.data and 'institution' in self.data:
      try:
        state_id = int(self.data.get('state'))
        location_id = int(self.data.get('location'))
        
        self.fields['location'].queryset = Location.objects.filter(state__id=state_id)
        self.fields['institution'].queryset = Institution.objects.filter(state__id=state_id, location__id=location_id)
      except (ValueError, TypeError):
        pass
    elif self.instance.state:
      self.fields['location'].queryset = self.instance.state.location_state
      self.fields['institution'].queryset = self.instance.location.institution_location

class ActivateSubscriptionForm(forms.Form):
  PACKAGES =(
    (2000, "SPOTLIGHT"),
    (5000, "HIGHLIGHT"),
    (10000, "FEATURED"),
  )
  # seller = forms.ModelChoiceField()
  package = forms.ChoiceField(
    widget=forms.RadioSelect,
    choices=PACKAGES
  )
  duration = forms.IntegerField(
    widget=forms.TextInput(attrs={'placeholder': 'Duration in Months'})
  )
  total = forms.DecimalField(
    widget=forms.TextInput(attrs={'readonly':'readonly'})
  )
  
