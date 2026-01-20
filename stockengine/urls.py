from django.contrib import admin
from django.urls import path
from core.views import returns_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("returns/", returns_api),
]
