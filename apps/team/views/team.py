from rest_framework import viewsets, status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.team.models import Team, StudentToTeam, TeacherToTeam
from apps.team.serializers import TeamSerializer, AllTeamSerializer, TeamUpdateSerializer
import logging

from utils.BaseView import BaseModelViewSet

# logger = logging.getLogger('team')
logger_security = logging.getLogger('security')

class TeamViewSet(BaseModelViewSet):
    queryset = Team.objects.filter(state=1)
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """根据不同的action返回不同的queryset"""
        if self.action == 'list_my_team':
            # 只返回当前用户所在的团队
            team_sn_list = StudentToTeam.objects.filter(
                student=self.request.sn,
                state=1
            ).values_list('team', flat=True)
            return Team.objects.filter(sn__in=team_sn_list, state=1)
        return super().get_queryset()

    @action(detail=False, methods=['get'])
    def list_my_team(self, request):
        """查看我的团队"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": 200, "data": serializer.data})

    @action(detail=False, methods=['get'])
    def list_all_team(self, request):
        """查看所有团队(简化版)"""
        queryset = self.filter_queryset(Team.objects.all())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AllTeamSerializer(queryset, many=True)
        return Response({"code": 200, "data": serializer.data})

    @action(detail=True, methods=['delete'])
    def dismiss_team(self, request, pk=None):
        """删除团队"""
        team = self.get_object()
        if team.cap != request.sn:
            return Response({"message": "您没有权限删除该团队", "code": 403})
        team.delete()
        team.save()

        return Response({"message": "团队已解散", "code": 200})


    @action(detail=True, methods=['put'])
    def update_team(self, request, pk=None):
        """更新团队信息（只有队长可以操作）"""
        team = Team.objects.get(id=pk, state=1)

        # 检查当前用户是否是队长
        if str(team.cap) != str(request.sn):
            logger_security.warning(f"用户 {request.username} 尝试修改其他团队信息 (团队ID: {pk})")
            # logger.info(f"用户 {request.username} 尝试修改其他团队信息 (团队ID: {pk})")
            return Response({"message": "您没有权限修改该团队信息", "code": 403})

        serializer = TeamUpdateSerializer(team, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({"message": "团队信息已更新", "code": 200, "data": serializer.data})