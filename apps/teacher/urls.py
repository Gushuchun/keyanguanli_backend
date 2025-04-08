from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherInfoViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'info', TeacherInfoViewSet, basename='info')

urlpatterns = [
    path('', include(router.urls)),
]