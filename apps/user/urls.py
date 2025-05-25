from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (Register, LoginView, SMS_Send,
                    CodeLoginView, ResetPasswordView,
                    ForgotPasswordView, SearchView, GetPublicKey)

router = DefaultRouter(trailing_slash=True)
router.register(r'register', Register, basename='register')


urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('sms_send/', SMS_Send.as_view(), name='sms_send'),
    path('code_login/', CodeLoginView.as_view(), name='code_login'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('search/', SearchView.as_view(), name='search'),
    path('get-public-key/', GetPublicKey.as_view(), name='get_public_key'),
]