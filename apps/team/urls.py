from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, TeamInviteViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'', TeamViewSet, basename='team')

# 添加自定义action的显式路径
urlpatterns = [
    path('create-team/', TeamInviteViewSet.as_view({'post': 'create_team'}), name='create-team'),
    path('confirm-team/', TeamInviteViewSet.as_view({'post': 'confirm_team'}), name='confirm-team'),
    path('invite_new_member/', TeamInviteViewSet.as_view({'post': 'invite_new_member'}), name='invite'),
    path('invite_new_teacher/', TeamInviteViewSet.as_view({'post': 'invite_new_teacher'}), name='invite'),
    path('myteam/', TeamViewSet.as_view({'get': 'list_my_team'}), name='my-team'),
    path('allteam/', TeamViewSet.as_view({'get': 'list_all_team'}), name='all-team'),
    path('dismiss/<int:pk>/', TeamViewSet.as_view({'delete': 'dismiss_team'}), name='dismiss-team'),
    path('update/<int:pk>/', TeamViewSet.as_view({'put': 'update_team'}), name='update-team'),
    path('quit/<int:pk>/', TeamViewSet.as_view({'put': 'quit_team'}), name='quit-team')
] + router.urls