from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("base.urls")),
    path("", include("user.urls")),
    path("store/", include("store.urls")),
    path('accounts/', include('allauth.urls')), 
    
    # path('dj-auth/', include('django.contrib.auth.urls')), # This was added because of the password confirm
    # path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    
]

tailwind_urlpattern = [
    path("__reload__/", include("django_browser_reload.urls")),   
    path("__debug__/", include("debug_toolbar.urls")),
]

if settings.DEBUG:
    urlpatterns += tailwind_urlpattern
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
