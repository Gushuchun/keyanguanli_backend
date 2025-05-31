import json

from rest_framework import serializers
from ..models import Patent, Inventor
from utils.service.minio_utils import upload_patent_file_to_minio
from ...student.models import Student
from ...teacher.models import Teacher


class InventorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventor
        fields = ['id', 'sn', 'name', 'phone', 'email']


class PatentSerializer(serializers.ModelSerializer):
    inventors = serializers.SerializerMethodField()

    class Meta:
        model = Patent
        fields = ['id', 'sn', 'number', 'name', 'date', 'description',
                  'patent_type', 'applicant_name', 'applicant_phone',
                  'applicant_email', 'applicant_sn', 'file', 'inventors']

    def get_inventors(self, obj):
        inventors = Inventor.objects.filter(patent=obj.sn, state=1)
        return InventorSerializer(inventors, many=True).data


class PatentCreateSerializer(serializers.ModelSerializer):
    inventors = serializers.JSONField(required=True)
    file = serializers.FileField(required=True)

    class Meta:
        model = Patent
        fields = ['number', 'name', 'date', 'patent_type', 'description', 'file', 'inventors']

    def validate_inventors(self, value):
        """验证发明人数据格式"""
        try:
            inventors = json.loads(value) if isinstance(value, str) else value
            if not isinstance(inventors, list):
                raise serializers.ValidationError("发明人数据必须是列表")

            for inventor in inventors:
                if not all(key in inventor for key in ['name', 'phone', 'email']):
                    raise serializers.ValidationError("发明人信息不完整")
        except json.JSONDecodeError:
            raise serializers.ValidationError("发明人数据格式不正确")
        return inventors

    def create(self, validated_data):
        inventors_data = validated_data.pop('inventors', [])
        uploaded_file = validated_data.pop('file')

        try:
            # 上传文件到MinIO
            file_url = upload_patent_file_to_minio(uploaded_file)

            # 从上下文中获取当前用户信息
            user = self.context['request'].user
            if user.role == 'student':
                student = Student.objects.get(username=user.username)
                sn = student.sn
            elif user .role == 'teacher':
                teacher = Teacher.objects.get(username=user.username)
                sn = teacher.sn
            else:
                raise serializers.ValidationError("Invalid user role")

            patent = Patent.objects.create(
                applicant_name=user.username,
                applicant_phone=user.tel,
                applicant_email=user.email,
                applicant_sn=sn,
                file=file_url,
                **validated_data
            )

            # 批量创建发明人
            inventors = [
                Inventor(
                    patent=patent.sn,
                    name=inventor['name'],
                    phone=inventor['phone'],
                    email=inventor['email']
                ) for inventor in inventors_data
            ]
            Inventor.objects.bulk_create(inventors)

            return patent
        except Exception as e:
            raise serializers.ValidationError(f"文件上传失败: {str(e)}")


class PatentUpdateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)

    class Meta:
        model = Patent
        fields = ['number', 'name', 'date', 'description', 'patent_type', 'file',
                  'applicant_name', 'applicant_phone', 'applicant_email',]
        extra_kwargs = {
            'number': {'required': False},
            'name': {'required': False},
            'date': {'required': False},
            'description': {'required': False},
            'patent_type': {'required': False},
            'file': {'required': False},
            'applicant_name': {'required': False},
            'applicant_phone': {'required': False},
            'applicant_email': {'required': False},
        }