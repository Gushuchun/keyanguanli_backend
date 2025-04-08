from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.competition.models import Competition, CompetitionMemberConfirm
from apps.competition.serializers import CompetitionSerializer, CompetitionMemberConfirmSerializer, CompetitionUpdateSerializer
from apps.team.models import StudentToTeam, Team
from utils.BaseView import BaseModelViewSet
import logging
from rest_framework.decorators import action

logger = logging.getLogger('competition')
logger_security = logging.getLogger('security')

class CompetitionViewSet(BaseModelViewSet):
    queryset = Competition.objects.filter(state=1)
    serializer_class = CompetitionSerializer

    def get_serializer_class(self):
        if self.action == 'update':
            return CompetitionUpdateSerializer
        return CompetitionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 异常将由 BaseModelViewSet 统一处理
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "message": "比赛信息创建成功，等待成员确认",
            "competition_id": serializer.instance.id
        }, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        """删除比赛（软删除）"""
        instance = self.get_object()  # 获取比赛实例
        if instance.get_cap(instance.id) != request.sn:
            print(request.sn)
            print(instance.get_cap(instance.id))
            logger_security.warning(f"用户 {request.sn} 尝试删除比赛: {instance.id}")
            return Response({"message": "只有队长可以删除比赛", "code": 403})

        instance.delete()  # 删除比赛实例
        return Response({
            "message": "比赛已成功删除",
            "data": {"id": instance.id},
            "code": 200
        })

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # 权限校验：仅队长可修改
        if instance.get_cap(instance.id) != request.sn:
            logger_security.warning(f"用户 {request.sn} 尝试修改比赛: {instance.id}")
            return Response({"message": "只有队长可以修改比赛", "code": 403})

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": "比赛信息更新成功",
            "data": serializer.data,
            "code": 200
        })

    @action(detail=False, methods=['get'], url_path='my')
    def my_competitions(self, request):

        # 1. 获取用户已确认的比赛ID列表（包括作为学生和老师）
        confirmed_as_student = CompetitionMemberConfirm.objects.filter(
            student=request.sn,
            status='confirmed',
            state=1
        ).values_list('sn', flat=True)

        confirmed_as_teacher = CompetitionMemberConfirm.objects.filter(
            teacher=request.sn,
            status='confirmed',
            state=1
        ).values_list('sn', flat=True)

        # 合并并去重
        all_competition_ids = list(set(confirmed_as_student) | set(confirmed_as_teacher))

        # 2. 获取完整的比赛信息
        competitions = Competition.objects.filter(
            sn__in=all_competition_ids,
            state=1
        ).order_by('-date')  # 按日期降序

        # 3. 分页处理
        page = self.paginate_queryset(competitions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(competitions, many=True)
        return Response({
            "message": "获取成功",
            "data": serializer.data,
            "code": 200
        })

    @action(detail=False, methods=['get'], url_path='team')
    def team_competitions(self, request):
        """查看指定团队的比赛"""
        # 1. 获取前端传来的team_id参数
        team_id = request.query_params.get('team_id')
        if not team_id:
            return Response({
                "message": "缺少team_id参数",
                "code": 400
            })

        # 3. 查询该团队的所有比赛
        competitions = Competition.objects.filter(
            team_id=team_id,
            state=1
        ).order_by('-date')  # 按比赛日期降序排列

        # 4. 分页处理
        page = self.paginate_queryset(competitions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(competitions, many=True)
        return Response({
            "message": "获取成功",
            "data": serializer.data,
            "code": 200
        })

    @action(detail=False, methods=['get'], url_path='all')
    def all_competitions(self, request):
        competitions = Competition.objects.filter(state=1)
        serializer = self.get_serializer(competitions, many=True)
        page = self.paginate_queryset(competitions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response({"message": "获取成功", "data": serializer.data, "code": 200})


class CompetitionConfirmViewSet(BaseModelViewSet):
    queryset = CompetitionMemberConfirm.objects.all()
    serializer_class = CompetitionMemberConfirmSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Only allow updating status and note fields
        data = {
            'note': request.data.get('note', instance.note)
        }

        if 'status' in request.data:
            data['status'] = request.data.get('status')

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)