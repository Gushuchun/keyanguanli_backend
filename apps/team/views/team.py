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
    TeamTeacherConfirmSerializer, TeamDetailSerializer
)
from .baseView import BaseConfirmViewSet, BaseTeamViewSet
from apps.team.serializers import BaseTeamSerializer
from ...competition.models import Competition
from ...student.models import Student
from ...teacher.models import Teacher


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
        com = request.query_params.get('com')
        filter = request.query_params.get('filter', '')
        status_filter = {
            'confirmed': ['confirmed'],
            'pending': ['pending'],
            'expired': ['expired']
        }.get(filter, ['pending', 'confirmed', 'expired'])
        if request.role == 'student':
            team_sns = StudentToTeam.objects.filter(
                student=request.sn,
                state=1,
                status__in=['pending', 'confirmed', 'expired']
            ).values_list('team', flat=True)
            if com:
                queryset = Team.objects.filter(sn__in=team_sns, state=1, status='confirmed').order_by('-create_time')
                serializer = self.get_serializer(queryset, many=True)
                return Response({
                    "code": status.HTTP_200_OK,
                    "data": serializer.data
                })
        elif request.role == 'teacher':
            team_sns = TeacherToTeam.objects.filter(
                teacher=request.sn,
                state=1,
                status__in=['pending', 'confirmed', 'expired']
            ).values_list('team', flat=True)

        queryset = self.filter_queryset(
            self.get_queryset().filter(sn__in=team_sns, status__in=status_filter)
        )

        # 检查团队状态和成员状态
        for team in queryset:
            if team.status == 'confirmed':
                if request.role == 'student':
                    member_status = StudentToTeam.objects.filter(
                        team=team.sn,
                        student=request.sn,
                        state=1
                    ).values_list('status', flat=True).first()
                elif request.role == 'teacher':
                    member_status = TeacherToTeam.objects.filter(
                        team=team.sn,
                        teacher=request.sn,
                        state=1
                    ).values_list('status', flat=True).first()

                if member_status == 'pending':
                    team.status = 'pending'

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": status.HTTP_200_OK,
            "data": serializer.data
        })

    # @action(detail=True, methods=['get'])
    def retrieve(self, request, *args, **kwargs):
        """获取团队详细信息"""
        team = self.get_object()
        serializer = TeamDetailSerializer(team)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['post'], url_path='remove-student')
    def remove_student(self, request):
        """移除学生"""
        team_sn = request.data.get('team_sn')
        student_sn = request.data.get('student_sn')
        try:
            # 检查队长权限
            team = Team.objects.get(sn=team_sn)
            self.check_captain_permission(team)
            student = StudentToTeam.objects.filter(team=team_sn, student=student_sn, state=1)
            if not student.exists():
                return Response({
                    "code": 400,
                    "message": "学生不存在"
                })
            student = student.first()
            student.delete()
            team.people_num -= 1
            student.save()
            team.save()
            return Response({
                "code": 200,
                "message": "移除成功"
            })
        except Exception as e:
            print(e)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "移除失败"
            })

    @action(detail=False, methods=['post'], url_path='remove-teacher')
    def remove_teacher(self, request):
        """移除学生"""
        team_sn = request.data.get('team_sn')
        teacher_sn = request.data.get('teacher_sn')
        try:
            # 检查队长权限
            team = Team.objects.get(sn=team_sn)
            self.check_captain_permission(team)
            teacher = TeacherToTeam.objects.filter(team=team_sn, teacher=teacher_sn, state=1)
            if not teacher.exists():
                return Response({
                    "code": 400,
                    "message": "学生不存在"
                })
            teacher = teacher.first()
            teacher.delete()
            team.people_num -= 1
            teacher.save()
            team.save()
            return Response({
                "code": 200,
                "message": "移除成功"
            })
        except Exception as e:
            print(e)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "移除失败"
            })

    @action(detail=False, methods=['get'], url_path='team-confirm-status')
    def team_confirm_status(self, request):
        """获取团队成员和老师的确认状态"""
        team_sn = request.query_params.get('team_sn')
        if not team_sn:
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "缺少团队SN参数"
            })

        # 获取学生确认状态
        students = StudentToTeam.objects.filter(team=team_sn, state=1)
        students_info = []
        for student in students:
            student_info = Student.objects.get(sn=student.student, state=1)
            students_info.append({
                'username': student_info.username,
                'sn': student_info.sn,
                'id': student.id,
                'status': student.status,
                'avatar': student_info.avatar
            })

        # 获取老师确认状态
        teachers = TeacherToTeam.objects.filter(team=team_sn, state=1)
        teachers_info = []
        for teacher in teachers:
            teacher_info = Teacher.objects.get(sn=teacher.teacher, state=1)
            teachers_info.append({
                'username': teacher_info.username,
                'sn': teacher_info.sn,
                'id': teacher.id,
                'status': teacher.status,
                'avatar': teacher_info.avatar,
            })

        return Response({
            "code": status.HTTP_200_OK,
            "data": {
                "students": students_info,
                "teachers": teachers_info
            }
        })

    @action(detail=False, methods=['get'], url_path='all-team-competition')
    def all_team_competition(self, request):
        """获取所有团队的比赛"""
        teams = Team.objects.filter(state=1,  status='confirmed')
        team_competitions = []
        for team in teams:
            competitions = Competition.objects.filter(team_sn=team.sn, state=1, status='confirmed')
            competition_details = []
            for competition in competitions:
                competition_details.append({
                    'competition_id': competition.id,
                    'competition_sn': competition.sn,
                    'title': competition.title,
                    'description': competition.description,
                    'team_sn': competition.team_sn,
                    'score': competition.score,
                    'date': competition.date,
                    'file': competition.file
                })
            team_competitions.append({
                'team_id': team.id,
                'team_name': team.name,
                'team_sn': team.sn,
                'competition_count': competitions.count(),
                'prize_count': team.prize_num,
                'people_count': team.people_num,
                'competitions': competition_details
            })

        # 按照 prize_count 从大到小排序
        team_competitions.sort(key=lambda x: x['prize_count'], reverse=True)

        return Response({
            "code": status.HTTP_200_OK,
            "data": team_competitions
        })

    @action(detail=False, methods=['post'], url_path='get-team-info')
    def get_team_info(self, request):
        """获取团队信息"""
        team_sn = request.data.get('team_sn')
        if not team_sn:
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "缺少团队SN参数"
            })

        try:
            team = Team.objects.get(sn=team_sn)
            serializer = TeamDetailSerializer(team)
            return Response({
                "code": status.HTTP_200_OK,
                "data": serializer.data
            })
        except Team.DoesNotExist:
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "团队不存在"
            })

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """根据关键字从自己的团队中搜索"""
        search_key = request.query_params.get('key', '')
        if not search_key:
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "缺少搜索关键字"
            })

        if request.role == 'student':
            team_sns = StudentToTeam.objects.filter(
                student=request.sn,
                state=1,
                status__in=['pending', 'confirmed']
            ).values_list('team', flat=True)
        elif request.role == 'teacher':
            team_sns = TeacherToTeam.objects.filter(
                teacher=request.sn,
                state=1,
                status__in=['pending', 'confirmed']
            ).values_list('team', flat=True)

        queryset = self.filter_queryset(
            self.get_queryset().filter(
                sn__in=team_sns,
                name__icontains=search_key,
                state=1
            )
        )

        for team in queryset:
            if team.status == 'confirmed':
                if request.role == 'student':
                    member_status = StudentToTeam.objects.filter(
                        team=team.sn,
                        student=request.sn,
                        state=1
                    ).values_list('status', flat=True).first()
                elif request.role == 'teacher':
                    member_status = TeacherToTeam.objects.filter(
                        team=team.sn,
                        teacher=request.sn,
                        state=1
                    ).values_list('status', flat=True).first()

                if member_status == 'pending':
                    team.status = 'pending'

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": status.HTTP_200_OK,
            "data": serializer.data
        })

class TeamStudentConfirmViewSet(BaseConfirmViewSet):
    """学生确认视图集"""
    queryset = StudentToTeam.objects.all()
    serializer_class = TeamStudentConfirmSerializer


class TeamTeacherConfirmViewSet(BaseConfirmViewSet):
    """老师确认视图集"""
    queryset = TeacherToTeam.objects.all()
    serializer_class = TeamTeacherConfirmSerializer