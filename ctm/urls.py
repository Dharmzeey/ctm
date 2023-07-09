from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView,SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("base.urls")),
    path("", include("user.urls")),
    path("store/", include("store.urls")),
    path("api/", include("api.urls")),    
    path('accounts/', include('allauth.urls')),    
]

spectacular_urlpatterns = [
  path('docs/schema/', SpectacularAPIView.as_view(), name='schema'),
  # Optional UI:
  path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
  path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc')
]
urlpatterns += spectacular_urlpatterns

tailwind_urlpattern = [
    path("__reload__/", include("django_browser_reload.urls")),   
]

if settings.DEBUG:
    urlpatterns += tailwind_urlpattern
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
