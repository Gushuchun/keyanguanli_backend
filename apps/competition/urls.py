from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompetitionViewSet, CompetitionTeacherConfirmViewSet, CompetitionStudentConfirmViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'', CompetitionViewSet, basename='new-competition')
router.register(r'confirm-student', CompetitionStudentConfirmViewSet, basename='confirm-student-competition')
router.register(r'confirm-teacher', CompetitionTeacherConfirmViewSet, basename='confirm-teacher-competition')

urlpatterns = [
    path('', include(router.urls)),
]