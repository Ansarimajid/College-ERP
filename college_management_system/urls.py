from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.views.static import serve
from . import settings

from main_app.views import SafePasswordResetView

urlpatterns = [
    path("", include('main_app.urls')),

    # Override Django's built-in password_reset with our safe version that
    # catches SMTP failures instead of returning HTTP 500.
    # Must be before the accounts/ include so it takes precedence.
    path(
        "accounts/password_reset/",
        SafePasswordResetView.as_view(),
        name='password_reset',
    ),

    path("accounts/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
]

# Serve uploaded media files (profile pictures, etc.) in all environments.
# Django's serve() view is used here because:
#   - static() helper returns [] when DEBUG=False, breaking production uploads.
#   - For a college ERP the traffic volume is low enough that Django serving
#     media is acceptable. For high traffic, replace with nginx or DO Spaces.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# In development also serve the static files via Django (not needed in
# production because WhiteNoise handles them at the WSGI layer).
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
