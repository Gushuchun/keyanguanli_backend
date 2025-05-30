from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminCompetitionViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'competition', AdminCompetitionViewSet, basename='competition')

urlpatterns = [
    path('', include(router.urls)),
]