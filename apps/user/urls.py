from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Register, LoginView

router = DefaultRouter(trailing_slash=True)
router.register(r'register', Register, basename='register')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
]