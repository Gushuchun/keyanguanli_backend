from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompetitionViewSet, CompetitionConfirmViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'', CompetitionViewSet, basename='new-competition')
router.register(r'confirm', CompetitionConfirmViewSet, basename='confirm-competition')

urlpatterns = [
    path('', include(router.urls)),
]