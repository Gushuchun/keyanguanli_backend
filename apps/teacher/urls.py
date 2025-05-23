from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherInfoViewSet, TeacherList

router = DefaultRouter(trailing_slash=True)
router.register(r'info', TeacherInfoViewSet, basename='info')
router.register(r'', TeacherList, basename='teacher')

urlpatterns = [
    path('', include(router.urls)),
]