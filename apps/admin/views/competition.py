from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from apps.competition.models import Competition
from apps.competition.serializers.competition import CompetitionDetailSerializer
from utils.base.baseView import BaseModelViewSet
from utils.permission import IsSuperAdminUser

class AdminCompetitionViewSet(BaseModelViewSet):
    """管理员比赛视图集"""
    queryset = Competition.objects.filter(state=1).order_by('-create_time')
    serializer_class = CompetitionDetailSerializer
    permission_classes = [IsSuperAdminUser]

    # 添加分页类
    pagination_class = PageNumberPagination

    def list(self, request, *args, **kwargs):
        """管理员获取所有比赛列表"""
        queryset = self.filter_queryset(self.get_queryset())

        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "获取成功"
        })

    def retrieve(self, request, *args, **kwargs):
        """管理员获取比赛详细信息"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "获取成功"
        })

    def update(self, request, *args, **kwargs):
        """管理员更新比赛信息"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "code": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "更新成功"
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        """管理员搜索比赛"""
        search_key = request.query_params.get('key', '')
        if not search_key:
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "缺少搜索关键字"
            })

        queryset = self.filter_queryset(
            self.get_queryset().filter(
                title__icontains=search_key,
                state=1
            )
        ).order_by('-create_time')

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "搜索成功"
        })
