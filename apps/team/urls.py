from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, TeamStudentConfirmViewSet, TeamTeacherConfirmViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'', TeamViewSet, basename='team')
router.register(r'confirm-student', TeamStudentConfirmViewSet, basename='confirm-student')
router.register(r'confirm-teacher', TeamTeacherConfirmViewSet, basename='confirm-teacher')


# 添加自定义action的显式路径
urlpatterns = [
    path('', include(router.urls)),
]