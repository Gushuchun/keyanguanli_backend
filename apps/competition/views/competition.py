from rest_framework.decorators import action
from apps.competition.models import Competition, StudentToCompetition, TeacherToCompetition
from apps.competition.serializers import (
    CompetitionMemberConfirmSerializer,
    CompetitionTeacherConfirmSerializer
)
from .BaseView import *


class CompetitionViewSet(BaseCompetitionViewSet):
    """竞赛视图集"""

    @action(detail=False, methods=['get'])
    def my(self, request):
        """获取当前用户参与的比赛"""
        if request.role == 'teacher':
            competition_sns = TeacherToCompetition.objects.filter(
                teacher=request.sn,
                state=1,
                status='confirmed'
            ).values_list('competition', flat=True)
        else:
            competition_sns = StudentToCompetition.objects.filter(
                student=request.sn,
                state=1,
                status='confirmed'
            ).values_list('competition', flat=True)

        queryset = self.filter_queryset(
            self.get_queryset().filter(sn__in=competition_sns)
        )
        return self.paginate_and_serialize_queryset(queryset)

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


class CompetitionStudentConfirmViewSet(BaseConfirmViewSet):
    """学生确认视图集"""
    queryset = StudentToCompetition.objects.all()
    serializer_class = CompetitionMemberConfirmSerializer


class CompetitionTeacherConfirmViewSet(BaseConfirmViewSet):
    """老师确认视图集"""
    queryset = TeacherToCompetition.objects.all()
    serializer_class = CompetitionTeacherConfirmSerializer