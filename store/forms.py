from django import forms
from .models import Store, Product, ProductImage
from user.models import Institution, Location
from .models import Catergory, SubCategory

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
    
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['subcategory'].queryset = SubCategory.objects.none()
    
    if 'category' in self.data and 'subcategory' in self.data:
      try:
        category_id = int(self.data.get('category'))
        self.fields['subcategory'].queryset = SubCategory.objects.filter(category__id=category_id)
      except (ValueError, TypeError):
        pass
    elif self.instance.category:
      self.fields['subcategory'].queryset = self.instance.category.subcategory_category
    
    
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
    self.request = kwargs.pop('request', None)
    super().__init__(*args, **kwargs)
    self.fields['location'].queryset = Location.objects.none()
    self.fields['institution'].queryset = Institution.objects.none()
    
    viewing_institution = self.request.session.get("viewing_institution", None)
    viewing_location = self.request.session.get("viewing_location", None)
    viewing_state = self.request.session.get("viewing_state", None)
    print(viewing_state)
    
    # if viewing_institution:
    #   # self.fields['state'].queryset = State.objects.get(id=viewing_state)
    #   self.fields['location'].queryset = Location.objects.filter(state=viewing_state)
    #   self.fields['institution'].queryset = Institution.objects.filter(state=viewing_state, location=viewing_location)
      
    # if viewing_location:
    #   # self.fields['state'].queryset = State.objects.get(id=viewing_state)
    #   self.fields['location'].queryset = Location.objects.filter(state=viewing_state)
      
    # if viewing_state:
      # self.fields['state'].queryset = State.objects.filter(id=viewing_state)


from django.forms.models import inlineformset_factory

ProductImageFormSet = inlineformset_factory(Product, ProductImage, fields=('image',), extra=0, edit_only=True)
