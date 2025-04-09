from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentInfoViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'info', StudentInfoViewSet, basename='info')

urlpatterns = [
    path('', include(router.urls)),
# path('info/update_avatar/', StudentInfoViewSet.as_view({'post': 'update_avatar'}), name='update_avatar'),
]