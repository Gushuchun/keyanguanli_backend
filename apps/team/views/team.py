from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.team.models import Team, StudentToTeam, TeacherToTeam
from apps.team.serializers import (
    TeamCreateSerializer,
    TeamMemberInviteSerializer,
    TeamTeacherInviteSerializer,
    TeamStudentConfirmSerializer,
    TeamTeacherConfirmSerializer
)
from .baseView import BaseConfirmViewSet, BaseTeamViewSet
from apps.team.serializers import BaseTeamSerializer

class TeamViewSet(BaseTeamViewSet):
    """团队视图集"""

    def create(self, request, *args, **kwargs):
        serializer = TeamCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            team = serializer.save()
            return Response({
                "code": status.HTTP_200_OK,
                "message": "团队创建成功，邀请已发送",
                "data": BaseTeamSerializer(team).data
            })
        except Exception as e:
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "创建团队失败",
                "error": str(e)
            })

    @action(detail=False, methods=['get'])
    def my(self, request):
        """获取当前用户所属团队"""
        team_sns = StudentToTeam.objects.filter(
            student=request.sn,
            status='confirmed',
            state=1
        ).values_list('team', flat=True)

        queryset = self.filter_queryset(
            self.get_queryset().filter(sn__in=team_sns)
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": status.HTTP_200_OK,
            "data": serializer.data
        })

    @action(detail=True, methods=['post'])
    def quit(self, request, pk=None):
        """退出团队"""
        team = self.get_object()

        with transaction.atomic():
            relation = StudentToTeam.objects.filter(
                team=team.sn,
                student=request.sn,
                status='confirmed',
            ).first()

            if not relation:
                return Response({
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "您不在该团队中"
                })

            # 如果是队长，需要先转让队长权限才能退出
            if relation.is_cap:
                return Response({
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "队长请先转让权限再退出团队"
                })

            relation.delete()
            team.people_num -= 1
            team.save()

        return Response({
            "code": status.HTTP_200_OK,
            "message": "已成功退出团队"
        })

    @action(detail=False, methods=['post'], url_path='invite-new-student')
    def invite_member(self, request):
        """邀请新成员"""
        serializer = TeamMemberInviteSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            # 检查队长权限
            team = Team.objects.get(sn=serializer.validated_data['team_sn'])
            self.check_captain_permission(team)

            invite = serializer.save()
            return Response({
                "code": status.HTTP_200_OK,
                "message": "成员邀请已发送",
                "data": {
                    "invite_id": invite.id
                }
            })
        except Exception as e:
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "邀请发送失败",
                "error": str(e)
            })

    @action(detail=False, methods=['post'], url_path='invite-new-teacher')
    def invite_teacher(self, request):
        """邀请新老师"""
        serializer = TeamTeacherInviteSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            # 检查队长权限
            team = Team.objects.get(sn=serializer.validated_data['team_sn'])
            self.check_captain_permission(team)

            invite = serializer.save()
            return Response({
                "code": status.HTTP_200_OK,
                "message": "老师邀请已发送",
                "data": {
                    "invite_id": invite.id
                }
            })
        except Exception as e:
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "邀请发送失败",
                "error": str(e)
            })


class TeamStudentConfirmViewSet(BaseConfirmViewSet):
    """学生确认视图集"""
    queryset = StudentToTeam.objects.all()
    serializer_class = TeamStudentConfirmSerializer


class TeamTeacherConfirmViewSet(BaseConfirmViewSet):
    """老师确认视图集"""
    queryset = TeacherToTeam.objects.all()
    serializer_class = TeamTeacherConfirmSerializer