from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.team.serializers import TeamCreateSerializer, TeamConfirmSerializer, TeamInviteNewMemberSerializer,TeamInviteNewTeacherSerializer
from apps.team.models import Team

class TeamInviteViewSet(viewsets.ViewSet):
    def create_team(self, request):
        """
        创建团队并发送邀请
        POST /api/team/create-team/
        {
            "name": "团队名称",
            "member_ids": ["1", "2", "3"],
            "teacher_id": "4"
        }
        """
        serializer = TeamCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            team = serializer.save()
            return Response({
                "message": "团队创建成功，邀请已发送",
                "team_id": team.id,
                "team_sn": team.sn,
                "team_name": team.name
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": "创建团队失败",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def confirm_team(self, request):
        """
        确认团队邀请
        POST /api/team/confirm-team/
        {
            "team": "团队ID",
            "status": "accepted/rejected"
        }
        返回:
        - 如果还有未处理的邀请: {"status": "pending", "message": "等待其他成员确认"}
        - 如果团队激活成功: {"status": "activated", "team": {...}, "members": [...]}
        - 如果团队被删除: {"status": "rejected", "message": "所有邀请被拒绝，团队已删除"}
        """
        serializer = TeamConfirmSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = serializer.update(None, serializer.validated_data)

            if result['activated']:
                return Response({
                    "message": result['message'],
                    "team_id": result['team'].id,
                    "team_name": result['team'].name,
                }, status=status.HTTP_200_OK)
            elif result['team'] is None:
                return Response({
                    "message": result['message']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "message": result['message'],
                    "team_id": result['team'].id
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": "操作失败",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def invite_new_member(self, request):
        """
        邀请新成员
        POST /api/team/invite-new-member/
        {
            "team_id": "团队ID",
            "member_sn": "新成员的SN"
        }
        """
        serializer = TeamInviteNewMemberSerializer(
            data=request.data,
            context={'request': request}
        )

        team_id = request.data.get('team_id')
        team_cap = Team.objects.get(id=team_id).cap
        sn = request.sn

        if team_cap != sn:
            return Response({
                "message": "您不是队长，无法邀请新成员"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            invite = serializer.save()
            return Response({
                "message": "邀请已发送，等待成员确认",
                "invite_id": invite.id
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": "邀请失败",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def invite_new_teacher(self, request):
        """
        邀请新老师
        POST /api/team/invite-new-teacher/
        {
            "team_id": "团队ID",
            "teacher_sn": "新老师的SN"
        }
        """
        serializer = TeamInviteNewTeacherSerializer(
            data=request.data,
            context={'request': request}
        )

        team_id = request.data.get('team_id')
        team_cap = Team.objects.get(id=team_id).cap
        sn = request.sn

        if team_cap != sn:
            return Response({
                "message": "您不是队长，无法邀请新老师"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            invite = serializer.save()
            return Response({
                "message": "邀请已发送，等待老师确认",
                "invite_id": invite.id
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": "邀请失败",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

