from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.team.models import Team
from apps.team.serializers import (
    TeamUpdateSerializer, BaseTeamSerializer,
)
from utils.base.baseView import BaseModelViewSet


class BaseTeamViewSet(BaseModelViewSet):
    """团队基础视图集"""
    queryset = Team.objects.filter(state=1).order_by('-create_time')
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Team.objects.filter(state=1)

    def get_serializer_class(self):
        if self.action == 'update':
            return TeamUpdateSerializer
        return BaseTeamSerializer

    def perform_destroy(self, instance):
        """删除团队前的检查"""
        if str(instance.cap) != str(self.request.sn):
            raise PermissionDenied("您没有权限删除该团队")
        super().perform_destroy(instance)

    def check_captain_permission(self, team):
        """检查队长权限"""
        if str(team.cap) != str(self.request.sn):
            raise PermissionDenied("您不是队长，无权执行此操作")


class BaseConfirmViewSet(BaseModelViewSet):
    """确认基础视图集"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(status__in=['pending', 'confirmed'])

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "code": status.HTTP_200_OK,
            "data": serializer.data
        })