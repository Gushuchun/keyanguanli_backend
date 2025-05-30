from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from ..models import Patent, Inventor
from ..serializers import PatentSerializer, PatentCreateSerializer, PatentUpdateSerializer, InventorSerializer
from utils.base.baseView import BaseModelViewSet
from utils.service.minio_utils import upload_patent_file_to_minio, delete_files_from_minio
from apps.college.models import College
from apps.user.models import UserModel as User
from ...student.models import Student
from ...teacher.models import Teacher


class PatentViewSet(BaseModelViewSet):
    queryset = Patent.objects.filter(state=1)

    def get_serializer_class(self):
        if self.action == 'create':
            return PatentCreateSerializer
        elif self.action == 'update':
            return PatentUpdateSerializer
        return PatentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # 保存专利
            patent = serializer.save()

            # 根据用户角色获取学院信息
            if request.user.role == 'student':
                student = Student.objects.get(username=request.user.username)
                college_id = student.college_id
            elif request.user.role == 'teacher':
                teacher = Teacher.objects.get(username=request.user.username)
                college_id = teacher.college_id
            else:
                return self.error_response("用户角色不支持")

            if college_id:
                college = College.objects.get(id=college_id)
                college.patent_num += 1
                college.save()

            return self.success_response("专利申请成功")

        except (Student.DoesNotExist, Teacher.DoesNotExist, College.DoesNotExist):
            return self.error_response("用户或学院不存在")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if str(instance.applicant_sn) != str(request.user.get_sn):
            return self.error_response("只有申请人可以删除专利")

        try:
            if request.user.role == 'student':
                student = Student.objects.get(sn=instance.applicant_sn)
                college_id = student.college_id
            elif request.user.role == 'teacher':
                teacher = Teacher.objects.get(sn=instance.applicant_sn)
                college_id = teacher.college_id
            else:
                return self.error_response("用户角色不支持")

            if college_id:
                college = College.objects.get(id=college_id)
                college.patent_num -= 1
                college.save()

        except (User.DoesNotExist, Student.DoesNotExist, Teacher.DoesNotExist, College.DoesNotExist):
            return self.error_response("用户或学院不存在")

        # 将专利和关联发明人状态设为0
        instance.state = 0
        instance.save()
        Inventor.objects.filter(patent=instance.sn).update(state=0)

        return self.success_response("删除成功")

    @action(detail=True, methods=['get', 'post', 'put', 'delete'])
    def inventors(self, request, pk=None):
        """管理发明人"""
        patent = self.get_object()

        # 检查权限
        if str(patent.applicant_sn) != str(request.user.get_sn):
            return self.error_response("只有申请人可以管理发明人")

        if request.method == 'GET':
            inventors = Inventor.objects.filter(patent=patent.sn, state=1)
            serializer = InventorSerializer(inventors, many=True)
            return self.success_response(serializer.data)

        elif request.method == 'POST':
            serializer = InventorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(patent=patent.sn)
            return self.success_response(serializer.data)

        elif request.method == 'PUT':
            inventor_id = request.data.get('id')
            try:
                inventor = Inventor.objects.get(id=inventor_id, patent=patent.sn, state=1)
            except Inventor.DoesNotExist:
                return self.error_response("发明人不存在")

            serializer = InventorSerializer(inventor, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.success_response(serializer.data)

        elif request.method == 'DELETE':
            inventor_id = request.data.get('id')
            if not inventor_id:
                return self.error_response("参数错误")

            try:
                inventor = Inventor.objects.get(id=inventor_id, patent=patent.sn, state=1)
            except Inventor.DoesNotExist:
                return self.error_response("发明人不存在")

            inventor.state = 0
            inventor.save()
            return self.success_response("删除成功")

    @action(detail=False, methods=['get'])
    def my(self, request):
        """查看当前用户自己的专利(带分页)"""
        # 获取当前用户的sn
        user_sn = request.sn

        # 过滤当前用户的专利
        queryset = self.get_queryset().filter(applicant_sn=user_sn, state=1)

        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if str(instance.applicant_sn) != str(request.user.get_sn):
            return self.error_response("只有申请人可以修改专利信息")

        # 只处理传入的字段
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # 处理文件上传
        if 'file' in request.data and request.data['file']:
            try:
                new_file_url = upload_patent_file_to_minio(request.data['file'])
                if instance.file:
                    delete_files_from_minio(instance.file)
                serializer.validated_data['file'] = new_file_url
            except Exception as e:
                return self.error_response(str(e))

        self.perform_update(serializer)
        return self.success_response(serializer.data)