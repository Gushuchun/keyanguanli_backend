from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserSettingsViewSet

router = DefaultRouter(trailing_slash=True)

router.register(r'', UserSettingsViewSet, basename='settings')

urlpatterns = [
    path('', include(router.urls)),
]