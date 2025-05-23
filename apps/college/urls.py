from django.urls import path, include
from apps.college.views.college import CollegeViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=True)

router.register(r'', CollegeViewSet, basename='colleges')
urlpatterns = [
    path('', include(router.urls)),
]