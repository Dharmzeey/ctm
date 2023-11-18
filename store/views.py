from typing import Any
from django.shortcuts import render
from django.db.models import Q
from django.views import View
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.db import IntegrityError

from utilities.mixins import SubscriptionCheckMixin
from utilities.locations import filter_store

from .forms import StoreForm, ProductForm, FilterForm, ProductImageForm, EditProductImageForm
from .models import Store, Product, ProductImage, SubCategory

# When the store is clicked, it displays all the stores at random
class ListStores(ListView):
  model = Store
  template_name = "store/stores.html"
  context_object_name = "stores"
  queryset = Store.objects.all().order_by("?")
  def get_queryset(self):
    filtered_store = filter_store(self.request)['stores']
    stores = Store.objects.filter(id__in=filtered_store).order_by("?")
    return stores
  def get_context_data(self, **kwargs):
    form = FilterForm(request=self.request)
    context =  super().get_context_data(**kwargs)
    context["form"] = form
    context["place"] = filter_store(self.request)['place']
    return context
list_stores = ListStores.as_view()

# when in the store page and the state is clicked, it loads the location associated with the state and also when the location is clicked, it loads the institution associated with such location
def on_store_filter_load(request):
  return render(request, 'store/store-list.html', filter_store(request))


class SearchStore(ListView):
  model = Store
  template_name = "store/stores.html"
  context_object_name = "stores"
  def get_queryset(self):
    filtered_store = filter_store(self.request)['stores']
    q = self.request.GET.get("q", None)
    if q:
      return super().get_queryset().filter(
      Q(store_name__icontains=q) & Q (id__in=filtered_store),
      )
    else:
      return super().get_queryset().filter(id__in=filtered_store)
  def get_context_data(self, **kwargs: Any):
     context = super().get_context_data(**kwargs)
     context['place'] = filter_store(self.request)['place']
     return context
search_store = SearchStore.as_view()


class CreateStore(LoginRequiredMixin, SubscriptionCheckMixin, CreateView):
  template_name = "store/create-store.html"
  form_class = StoreForm
  model = Store
  
  def get(self, request, *args, **kwargs):
    if request.user.selling_vendor:
      try:
        store_name = self.request.user.selling_vendor.store_owner.store_name
        messages.error(self.request, "You Can not create another store as you already have one!!!")
        return redirect(reverse_lazy("store:detail_store", kwargs={'store_name': store_name}))
      except:
        return super().get(request, *args, **kwargs)
    
  def form_valid(self, form):
    form.instance.owner = self.request.user.selling_vendor
    form.save()
    return super().form_valid(form)

  def get_success_url(self):
    messages.success(self.request, "Store Details Updated")
    store_name = self.request.user.selling_vendor.store_owner.store_name
    return reverse_lazy("store:detail_store", kwargs={'store_name': store_name})
create_store = CreateStore.as_view()


class EditStore(LoginRequiredMixin, SubscriptionCheckMixin, UpdateView):
  template_name = "store/edit-store.html"
  form_class = StoreForm  
  model = Store
  def get_object(self):
    store = get_object_or_404(Store, owner=self.request.user.selling_vendor.id)
    return store
  
  def get_success_url(self):
    messages.success(self.request, "Store Details Updated")
    store_name = self.request.user.selling_vendor.store_owner.store_name
    return reverse_lazy("store:detail_store", kwargs={'store_name': store_name})
edit_store = EditStore.as_view()


class StoreDetails(SubscriptionCheckMixin, View):
  template_name = "store/store-details.html"
  def get(self, request, store_name):
    store = Store.objects.get(store_name__iexact=store_name)
    products = Product.objects.filter(store=store.id)
    # THIS IF BLOCK WILL EXECUTE IF THE PERSON CLICKNIG THE STORE IS ALSO THE OWNER
    if not request.user.is_anonymous and request.user.user_info.is_vendor and store.owner.seller == request.user:
      owner = Store.objects.get(owner__seller=request.user.id, store_name__iexact=store_name)
      context = {"owner": owner, "store": store, "products":products}
    else:
      context = {"store": store, "products":products}
    return render(request, self.template_name, context)
detail_store = StoreDetails.as_view()


def load_subcategory(request):
  category_id = request.GET.get('category')
  subcategories = SubCategory.objects.filter(category=category_id)
  context = {
    "subcategories": subcategories
  }
  return render(request, "store/subcategory-list.html", context)

class AddProduct(LoginRequiredMixin, SubscriptionCheckMixin, View):
  template_name = "store/add-product.html"
  def get(self, request, store_name): #store_name is used by the subscriptioncheckmixin
    form = ProductForm()
    form2 = ProductImageForm()
    max_image = int(request.user.selling_vendor.subscription_plan) // 1000
    context = {"form": form, "form2":form2, "max":max_image}
    return render(request, self.template_name, context)
  
  def post(self, request, store_name):
    max_image = int(request.user.selling_vendor.subscription_plan) // 1000
    form = ProductForm(request.POST, request.FILES)
    form2 = ProductImageForm(request.POST, request.FILES)
    images = request.FILES.getlist('image')
    if len(images) > max_image:
      messages.error(request, f"Only {max_image} images allowed")
      context = {"form": form, "form2":form2, "max":max_image}
      return render(request, self.template_name, context)
    if form.is_valid() and form2.is_valid():
      vendor = self.request.user.selling_vendor
      store = vendor.store_owner
      title = form.cleaned_data['title']
      description = form.cleaned_data['description']
      thumbnail = form.cleaned_data['thumbnail']
      price = form.cleaned_data['price']
      product_instance = Product.objects.create(
        vendor=vendor,
        store = store,
        title=title,
        description = description,
        thumbnail = thumbnail,
        price = price
      )
      product_instance.save()
      for i in images:
        product_image = ProductImage.objects.create(product=product_instance, image=i)
        product_image.save()
      store_name = self.request.user.selling_vendor.store_owner
      messages.info(request, "Product Added Sucessfully")
      return HttpResponseRedirect(reverse_lazy('store:detail_store', kwargs={'store_name': store_name}))
    messages.error(request, "Something went wrong")
    context = {"form": form, "form2":form2, "max":max_image}
    return render(request, self.template_name, context)
add_product = AddProduct.as_view()


class ProductDetails(SubscriptionCheckMixin, DetailView):
  template_name = "store/product-details.html"
  model = Product

  def get_object(self):
    store = get_object_or_404(Store, store_name=self.kwargs['store_name'])
    product = get_object_or_404(Product, uuid=self.kwargs['product_uuid'], store=store)
    return product
  
  def get_context_data(self, **kwargs):
    context =  super().get_context_data(**kwargs)
    product = self.get_object()    
    recently_viewed = self.request.session.get("recently_viewed", [])
    
    if str(product.uuid) not in recently_viewed:
      recently_viewed.append(str(product.uuid))
    self.request.session['recently_viewed'] = recently_viewed
    qs = Product.objects.filter(uuid__in=recently_viewed)[:5]
    
    sorted_qs = sorted(qs, key=lambda p: recently_viewed.index(str(p.uuid)))
    store_goods = Product.objects.filter(store=product.store).order_by("?")[:7]
    store = get_object_or_404(Store, store_name=self.kwargs['store_name'])
    
    context['more_items'] = store_goods
    context['recently_viewed'] = sorted_qs
    context['store'] = store
  
    return context
detail_product = ProductDetails.as_view()


# class EditProduct(LoginRequiredMixin, SubscriptionCheckMixin, UpdateView):
#   template_name = "store/edit-product.html"
#   model = Product
#   form_class = ProductForm
#   def get_object(self):
#     store = self.request.user.selling_vendor.store_owner
#     product = get_object_or_404(Product, uuid=self.kwargs['product_uuid'], store=store)
#     return product
#   def get_success_url(self):
#     messages.success(self.request, "Item Updated")
#     store_name = self.request.user.selling_vendor.store_owner
#     return reverse_lazy('store:detail_store', kwargs={'store_name': store_name})
# edit_product = EditProduct.as_view()


# class EditProduct(LoginRequiredMixin, SubscriptionCheckMixin, View):
#   template_name = "store/edit-product.html"
#   model = Product
#   # form = ProductForm
#   # form2 = ProductImageForm
  
#   def get(self, request, store_name, product_uuid):
#     product = Product.objects.get(uuid=product_uuid)
#     form = ProductForm(instance=product)
#     images = ProductImage.objects.filter(product=product)
#     list_image = []
#     for i in images:
#       list_image.append(EditProductImageForm(instance=i))
#     context = {"form": form, "form2": list_image}
#     return render(request, self.template_name, context)
  
#   def post(self, request, store_name, product_uuid):
#     max_image = int(request.user.selling_vendor.subscription_plan) // 1000
#     product = Product.objects.get(uuid=product_uuid)
#     form = ProductForm(request.POST, request.FILES, instance=product)
#     get_new_images = request.FILES.getlist("image")    
#     existing_images = ProductImage.objects.filter(product=product)
#     list_image = []
#     for i in existing_images:
#       list_image.append(EditProductImageForm(instance=i))
#     if len(get_new_images) > max_image:
#       messages.error(request, f"Only {max_image} images allowed")
#       context = {"form": form, "form2":list_image, "max":max_image}
#       return render(request, self.template_name, context)
    
#     if form.is_valid:
#       store_name = self.request.user.selling_vendor.store_owner
#       messages.info(request, "Product Updated Sucessfully")
#       product = form.save()
#       return HttpResponseRedirect(reverse_lazy('store:detail_store', kwargs={'store_name': store_name}))
#     messages.error(request, "Something went wrong")
#     return render()
# edit_product = EditProduct.as_view()

# COMING BACK TO THIS
from .forms import ProductImageFormSet
from django.db import transaction

class EditProductView(LoginRequiredMixin, SubscriptionCheckMixin, UpdateView):
    model = Product
    template_name = "store/edit-product.html"
    form_class = ProductForm
    
    def get_object(self):
      store = self.request.user.selling_vendor.store_owner
      product = get_object_or_404(Product, uuid=self.kwargs['product_uuid'], store=store)
      return product

    def get_context_data(self, **kwargs):
      data = super(EditProductView, self).get_context_data(**kwargs)
      if self.request.POST:
        data['product_images'] = ProductImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
      else:
        data['product_images'] = ProductImageFormSet(instance=self.object)
      return data

    def form_valid(self, form):
      context = self.get_context_data()
      product_images = context['product_images']
      with transaction.atomic():
        self.object = form.save()

        if product_images.is_valid():
          product_images.instance = self.object
          product_images.save()
      return super(EditProductView, self).form_valid(form)
    
    def get_success_url(self):
      messages.success(self.request, "Item Updated")
      store_name = self.request.user.selling_vendor.store_owner
      return reverse_lazy('store:detail_store', kwargs={'store_name': store_name})
edit_product = EditProductView.as_view()

class DeleteProduct(LoginRequiredMixin, SubscriptionCheckMixin, DeleteView):
  model = Product
  template_name = "store/delete-product.html"
  def get_object(self):
    store = self.request.user.selling_vendor.store_owner
    product = get_object_or_404(Product, uuid=self.kwargs['product_uuid'], store=store)
    return product

  def get_success_url(self):
    messages.success(self.request, "Item Deleted")
    store_name = self.request.user.selling_vendor.store_owner
    return reverse_lazy('store:detail_store', kwargs={'store_name': store_name})
delete_product = DeleteProduct.as_view()


def recently_viewed(request):
  if request.method == 'POST':
    return HttpResponse(status=200)
  else:
    return HttpResponse(status=405)


class MakePurchase(View):
  template_name = "store/purchase-page.html"
  def get(self, request, **kwargs):
    product_uuid = kwargs.get("product_uuid") 
    
    store_name = kwargs.get("store_name")
    
    return render(request, self.template_name)
make_purchase = MakePurchase.as_view()