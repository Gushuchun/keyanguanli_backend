from rest_framework import status
from apps.competition.models import Competition
from apps.competition.serializers import (
    CompetitionCreateSerializer,
    CompetitionUpdateSerializer,

)
from apps.competition.serializers.BaseSerializers import BaseCompetitionSerializer
from utils.base.baseView import BaseModelViewSet
from django.conf import settings

class BaseCompetitionViewSet(BaseModelViewSet):
    """竞赛基础视图集"""
    queryset = Competition.objects.filter(state=1).order_by('create_time')
    serializer_class = BaseCompetitionSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CompetitionCreateSerializer
        elif self.action == 'update':
            return CompetitionUpdateSerializer
        return super().get_serializer_class()

    def check_captain_permission(self, competition):
        """检查队长权限"""
        if competition.get_cap(competition.id) != self.request.sn:
            self.permission_denied(
                self.request,
                message="只有队长可以执行此操作",
                code=status.HTTP_403_FORBIDDEN
            )


class BaseConfirmViewSet(BaseModelViewSet):
    """确认基础视图集"""

    def get_queryset(self):
        return self.queryset.filter(state=1)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.success_response(serializer.data)