from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserInfoViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'info', UserInfoViewSet, basename='info')

urlpatterns = [
    path('', include(router.urls)),
]