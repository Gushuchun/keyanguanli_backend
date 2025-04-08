from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.competition.models import Competition, CompetitionMemberConfirm
from apps.competition.serializers import CompetitionSerializer, CompetitionMemberConfirmSerializer, CompetitionUpdateSerializer
from utils.BaseView import BaseModelViewSet
import logging

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

class CompetitionConfirmViewSet(BaseModelViewSet):
    queryset = CompetitionMemberConfirm.objects.all()
    serializer_class = CompetitionMemberConfirmSerializer

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # 只允许更新 status 和 note 字段
        data = {
            'status': request.data.get('status'),
            'note': request.data.get('note', instance.note)
        }

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)