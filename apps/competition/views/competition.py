from rest_framework.decorators import action
from rest_framework.response import Response

from apps.competition.models import Competition, StudentToCompetition, TeacherToCompetition
from apps.competition.serializers import (
    CompetitionMemberConfirmSerializer,
    CompetitionTeacherConfirmSerializer,
    CompetitionDetailSerializer, CompetitionTeacherInviteSerializer
)
from .BaseView import *
from ...student.models import Student
from ...teacher.models import Teacher
from ...team.models import Team


class CompetitionViewSet(BaseCompetitionViewSet):
    """竞赛视图集"""

    @action(detail=False, methods=['get'])
    def my(self, request):
        """获取当前用户参与的比赛"""
        if request.role == 'teacher':
            competition_sns = TeacherToCompetition.objects.filter(
                teacher=request.sn,
                state=1,
                status__in=['pending', 'confirmed', 'expired']
            ).values_list('competition', flat=True)
        else:
            competition_sns = StudentToCompetition.objects.filter(
                student=request.sn,
                state=1,
                status__in=['pending', 'confirmed', 'expired']
            ).values_list('competition', flat=True)

        queryset = self.filter_queryset(
            self.get_queryset().filter(sn__in=competition_sns)
        ).order_by('-create_time')
        return self.paginate_and_serialize_queryset(queryset)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索比赛"""
        query = request.query_params.get('query', '')
        queryset = self.filter_queryset(
            self.get_queryset().filter(name__icontains=query)
        )
        return self.paginate_and_serialize_queryset(queryset)

    @action(detail=False, methods=['post'], url_path='invite-new-teacher')
    def invite_teacher(self, request):
        """邀请新老师"""
        serializer = CompetitionTeacherInviteSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            # 检查队长权限
            competition = Competition.objects.get(sn=serializer.validated_data['competition_sn'])
            self.check_captain_permission(competition)

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

    @action(detail=False, methods=['post'], url_path='remove-teacher')
    def remove_teacher(self, request):
        """移除老师"""
        competition_sn = request.data.get('competition_sn')
        teacher_sn = request.data.get('teacher_sn')
        try:
            # 检查队长权限
            competition = Competition.objects.get(sn=competition_sn)
            self.check_captain_permission(competition)

            teacher = TeacherToCompetition.objects.filter(competition=competition_sn, teacher=teacher_sn, state=1)
            if not teacher.exists():
                return Response({
                    "code": 400,
                    "message": "老师不存在"
                })
            teacher = teacher.first()
            teacher.delete()
            competition.teacher_num -= 1
            teacher.save()
            competition.save()
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

    @action(detail=False, methods=['get'])
    def team(self, request):
        """获取指定团队的比赛"""
        team_id = request.query_params.get('team_id')
        if not team_id:
            return self.error_response("缺少team_id参数", status.HTTP_400_BAD_REQUEST)

        queryset = self.filter_queryset(
            self.get_queryset().filter(team_id=team_id)
        )
        return self.paginate_and_serialize_queryset(queryset)

    def retrieve(self, request, *args, **kwargs):
        """获取团队详细信息"""
        team = self.get_object()
        serializer = CompetitionDetailSerializer(team)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def all(self, request):
        """获取所有比赛"""
        return self.paginate_and_serialize_queryset(self.filter_queryset(self.get_queryset()))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_captain_permission(instance)  # 权限检查
        self.perform_destroy(instance)  # 执行删除
        return self.success_response(message="比赛删除成功")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        self.check_captain_permission(instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return self.success_response(
            data=serializer.data,
            message="比赛更新成功"
        )

    @action(detail=False, methods=['get'], url_path='competition-confirm-status')
    def competition_confirm_status(self, request):
        """获取团队成员和老师的确认状态"""
        competition_sn = request.query_params.get('competition_sn')
        if not competition_sn:
            return self.error_response(message="competition_sn")

        # 获取学生确认状态
        students = StudentToCompetition.objects.filter(competition=competition_sn, state=1)
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
        teachers = TeacherToCompetition.objects.filter(competition=competition_sn, state=1)
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

        return self.success_response(data={
            'students': students_info,
            'teachers': teachers_info
        }, message="获取确认状态成功")

    def list(self, request, *args, **kwargs):
        """获取比赛列表，并返回每场比赛所属团队的名称"""
        queryset = self.filter_queryset(self.get_queryset()).order_by('-date')
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        # 为每场比赛添加团队名称
        for competition in data:
            team = Team.objects.filter(sn=competition['team_sn']).first()
            competition['team_name'] = team.name if team else None
        return Response(data)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """根据关键字搜索比赛"""
        search_key = request.query_params.get('key', '')
        if not search_key:
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "缺少搜索关键字"
            })

        if request.role == 'teacher':
            competition_sns = TeacherToCompetition.objects.filter(
                teacher=request.sn,
                state=1,
                status__in=['pending', 'confirmed', 'expired']
            ).values_list('competition', flat=True)
        else:
            competition_sns = StudentToCompetition.objects.filter(
                student=request.sn,
                state=1,
                status__in=['pending', 'confirmed', 'expired']
            ).values_list('competition', flat=True)

        queryset = self.filter_queryset(
            self.get_queryset().filter(
                sn__in=competition_sns,
                title__icontains=search_key,
                state=1
            )
        ).order_by('-create_time')

        return self.paginate_and_serialize_queryset(queryset)


class CompetitionStudentConfirmViewSet(BaseConfirmViewSet):
    """学生确认视图集"""
    queryset = StudentToCompetition.objects.all()
    serializer_class = CompetitionMemberConfirmSerializer


class CompetitionTeacherConfirmViewSet(BaseConfirmViewSet):
    """老师确认视图集"""
    queryset = TeacherToCompetition.objects.all()
    serializer_class = CompetitionTeacherConfirmSerializer