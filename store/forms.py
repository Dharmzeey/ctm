from django import forms
from .models import Store, Product, ProductImage
from user.models import Institution, Location, State

class StoreForm(forms.ModelForm):
  class Meta:
    model = Store
    fields = "__all__"
    exclude = ("owner", )
    
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields["store_location"].queryset = Location.objects.none()
    self.fields["store_institution"].queryset = Institution.objects.none()
    
    if 'store_state' in self.data and 'store_location' in self.data and 'store_institution' in self.data:
      try:
        store_state_id = int(self.data.get('store_state'))
        store_location_id = int(self.data.get('store_location'))
        
        self.fields['store_location'].queryset = Location.objects.filter(state__id=store_state_id)
        self.fields['store_institution'].queryset = Institution.objects.filter(state__id=store_state_id, location__id=store_location_id)
      except (ValueError, TypeError):
        pass
    elif self.instance.store_state:
      self.fields['store_location'].queryset = self.instance.store_state.location_state
      self.fields['store_institution'].queryset = self.instance.store_location.institution_location


class ProductForm(forms.ModelForm):
  class Meta:
    model = Product
    fields = "__all__"
    exclude = ("vendor", "store", "uuid")
    
    widgets = {
      'description': forms.Textarea(attrs={'rows':'4'})
    }
    
    
class ProductImageForm(forms.ModelForm):
  class Meta:
    model = ProductImage
    fields = ["image"]
    widgets = {
      'image': forms.ClearableFileInput(attrs={"multiple": True, "accept": "image/*"})
    }
    
    labels ={
      'image': "Images"
    }
    

class EditProductImageForm(forms.ModelForm):
  class Meta:
    model = ProductImage
    fields = ["image"]
    widgets = {
      'image': forms.ClearableFileInput(attrs={"accept": "image/*"})
    }
    
    labels ={
      'image': "Image"
    }


class FilterForm(forms.ModelForm):
  institution = forms.ModelChoiceField(queryset=Institution.objects.none(), required=False)
  class Meta:
    model = Institution
    fields = ("state", "location", "institution")
    
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['location'].queryset = Location.objects.none()


from django.forms.models import inlineformset_factory

ProductImageFormSet = inlineformset_factory(Product, ProductImage, fields=('image',), extra=0, edit_only=True)
