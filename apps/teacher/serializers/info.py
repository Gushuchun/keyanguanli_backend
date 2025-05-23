from rest_framework import serializers
from apps.teacher.models import Teacher
import logging
from django.conf import settings

from apps.user.models import UserModel
from utils.service.minio_utils import upload_competition_image_to_minio, delete_files_from_minio

logger = logging.getLogger('teacher')

class TeacherInfoSerializer(serializers.ModelSerializer):
    college = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            'id', 'username', 'email',
            'gender', 'phone', 'college_id', 'avatar', 'college', 'note'
        ]
        extra_kwargs = {
            'username': {'read_only': True},
            'id': {'read_only': True},
            'college_id': {'read_only': True},
        }

    def get_college(self, obj):
        """根据 college_id 获取学院名称"""
        from apps.college.models import College
        college = College.objects.filter(id=obj.college_id).first()
        return college.name if college else None

    def update(self, instance, validated_data):

        # 更新字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # 同步更新User表中的数据
        user = UserModel.objects.get(username=instance.username)
        user.email = instance.email
        user.username = instance.username
        user.tel = instance.phone
        user.save()

        instance.save()
        return instance

class TeacherAvatarSerializer(serializers.ModelSerializer):

    avatar = serializers.FileField(required=True)

    class Meta:
        model = Teacher
        fields = ['avatar']
    def update(self, instance, validated_data):
        """处理头像上传"""
        avatar = validated_data.get('avatar')

        if avatar:
            # 上传头像到 MinIO 并获取图片 URL
            try:
                old_file_urls = instance.avatar
                image_urls = upload_competition_image_to_minio([avatar], prefix=settings.MINIO_STORAGE_MEDIA_AVATAR)
                if old_file_urls:
                    # 从 MinIO 中删除旧的头像
                    delete_files_from_minio(old_file_urls)
                file_urls = ",".join(image_urls)
                avatar_url = file_urls # 头像的访问 URL

                instance.avatar = avatar_url
                instance.save()
            except Exception as e:
                raise serializers.ValidationError(f"头像上传失败: {str(e)}")

        return instance