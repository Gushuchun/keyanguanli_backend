from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from ..models import Paper, Author
from ..serializers import PaperSerializer, PaperCreateSerializer, PaperUpdateSerializer, AuthorSerializer
from utils.base.baseView import BaseModelViewSet
from utils.service.minio_utils import upload_paper_file_to_minio, delete_files_from_minio
from apps.college.models import College
from apps.user.models import UserModel as User
from ...student.models import Student
from ...teacher.models import Teacher


class PaperViewSet(BaseModelViewSet):
    queryset = Paper.objects.filter(state=1)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaperCreateSerializer
        elif self.action == 'update':
            return PaperUpdateSerializer
        return PaperSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            paper = serializer.save()

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
                college.paper_num += 1
                college.save()

            return self.success_response("论文创建成功")

        except (Student.DoesNotExist, Teacher.DoesNotExist, College.DoesNotExist):
            return self.error_response("用户或学院不存在")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if str(instance.applicant_sn) != str(request.user.get_sn):
            return self.error_response("只有申请人可以修改论文信息")

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if 'file' in request.data and request.data['file']:
            try:
                new_file_url = upload_paper_file_to_minio(request.data['file'])
                if instance.file:
                    delete_files_from_minio(instance.file)
                serializer.validated_data['file'] = new_file_url
            except Exception as e:
                return self.error_response(str(e))

        self.perform_update(serializer)
        return self.success_response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if str(instance.applicant_sn) != str(request.user.get_sn):
            return self.error_response("只有申请人可以删除论文")

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
                college.paper_num -= 1
                college.save()

        except (User.DoesNotExist, Student.DoesNotExist, Teacher.DoesNotExist, College.DoesNotExist):
            return self.error_response("用户或学院不存在")

        instance.state = 0
        instance.save()
        Author.objects.filter(paper=instance.sn).update(state=0)

        return self.success_response("删除成功")

    @action(detail=True, methods=['get', 'post', 'put', 'delete'])
    def authors(self, request, pk=None):
        paper = self.get_object()

        if str(paper.applicant_sn) != str(request.user.get_sn):
            return self.error_response("只有申请人可以管理作者")

        if request.method == 'GET':
            authors = Author.objects.filter(paper=paper.sn, state=1)
            serializer = AuthorSerializer(authors, many=True)
            return self.success_response(serializer.data)

        elif request.method == 'POST':
            serializer = AuthorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(paper=paper.sn)
            return self.success_response(serializer.data)

        elif request.method == 'PUT':
            author_id = request.data.get('id')
            try:
                author = Author.objects.get(id=author_id, paper=paper.sn, state=1)
            except Author.DoesNotExist:
                return self.error_response("作者不存在")

            serializer = AuthorSerializer(author, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.success_response(serializer.data)

        elif request.method == 'DELETE':
            author_id = request.data.get('id')
            if not author_id:
                return self.error_response("参数错误")

            try:
                author = Author.objects.get(id=author_id, paper=paper.sn, state=1)
            except Author.DoesNotExist:
                return self.error_response("作者不存在")

            author.state = 0
            author.save()
            return self.success_response("删除成功")

    @action(detail=False, methods=['get'])
    def my(self, request):
        user_sn = request.sn

        queryset = self.get_queryset().filter(applicant_sn=user_sn, state=1)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(serializer.data)