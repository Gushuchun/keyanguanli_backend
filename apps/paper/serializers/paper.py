import json

from rest_framework import serializers
from ..models import Paper, Author
from utils.service.minio_utils import upload_paper_file_to_minio
from ...student.models import Student
from ...teacher.models import Teacher


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'sn', 'name', 'phone', 'email']


class PaperSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField()

    class Meta:
        model = Paper
        fields = ['id', 'sn', 'number', 'title', 'journal', 'publish_date',
                  'abstract', 'keywords', 'file', 'applicant_name',
                  'applicant_email', 'applicant_sn', 'authors']

    def get_authors(self, obj):
        authors = Author.objects.filter(paper=obj.sn, state=1)
        return AuthorSerializer(authors, many=True).data


class PaperCreateSerializer(serializers.ModelSerializer):
    authors = serializers.JSONField(required=True)
    file = serializers.FileField(required=True)

    class Meta:
        model = Paper
        fields = ['number', 'title', 'journal', 'publish_date', 'abstract',
                  'keywords', 'file', 'authors']

    def validate_authors(self, value):
        try:
            authors = json.loads(value) if isinstance(value, str) else value
            if not isinstance(authors, list):
                raise serializers.ValidationError("作者数据必须是列表")

            for author in authors:
                if not all(key in author for key in ['name', 'phone', 'email']):
                    raise serializers.ValidationError("作者信息不完整")
        except json.JSONDecodeError:
            raise serializers.ValidationError("作者数据格式不正确")
        return authors

    def create(self, validated_data):
        authors_data = validated_data.pop('authors', [])
        uploaded_file = validated_data.pop('file')

        try:
            file_url = upload_paper_file_to_minio(uploaded_file)
            user = self.context['request'].user

            if user.role == 'student':
                student = Student.objects.get(username=user.username)
                sn = student.sn
            elif user.role == 'teacher':
                teacher = Teacher.objects.get(username=user.username)
                sn = teacher.sn
            else:
                raise serializers.ValidationError("Invalid user role")

            paper = Paper.objects.create(
                applicant_name=user.username,
                applicant_email=user.email,
                applicant_sn=sn,
                file=file_url,
                **validated_data
            )

            authors = [
                Author(
                    paper=paper.sn,
                    name=author['name'],
                    phone=author['phone'],
                    email=author['email']
                ) for author in authors_data
            ]
            Author.objects.bulk_create(authors)

            return paper
        except Exception as e:
            raise serializers.ValidationError(f"文件上传失败: {str(e)}")


class PaperUpdateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)

    class Meta:
        model = Paper
        fields = ['number', 'title', 'journal', 'publish_date', 'abstract',
                  'keywords', 'file', 'applicant_name', 'applicant_email']
        extra_kwargs = {
            field: {'required': False} for field in fields
        }