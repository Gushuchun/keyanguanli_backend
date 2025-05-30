from django.conf import settings
from rest_framework import serializers
from apps.student.models import Student
import logging

from apps.user.models import UserModel
from utils.service.minio_utils import upload_competition_image_to_minio, delete_files_from_minio

logger = logging.getLogger('student')

class StudentSerializer(serializers.ModelSerializer):

    cn = serializers.CharField(write_only=True, required=False)
    cn_1 = serializers.SerializerMethodField()
    college = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'username', 'email',
            'gender', 'phone', 'cn',
            'cn_1',
            'prize_num', 'race_num', 'college_id', 'avatar', 'college', 'note'
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

    def get_cn_1(self, obj):
        """解密cn字段的方法"""
        try:
            # 调用模型的解密方法
            return obj.get_cn()
        except Exception as e:
            logger.error(f"解密身份证信息失败: {str(e)}")
            return None

    def update(self, instance, validated_data):
        """重写update方法，对身份证号码进行加密处理，并同步更新User表"""
        new_cn = validated_data.get('cn')
        if new_cn:
            try:
                # 调用模型的加密方法
                instance.set_cn(new_cn)
            except Exception as e:
                logger.error(f"加密身份证信息失败: {str(e)}")
                raise serializers.ValidationError({'cn': '身份证号码加密失败'})

        # 更新其他字段
        for attr, value in validated_data.items():
            if attr != 'cn':  # 已经处理了cn字段
                setattr(instance, attr, value)

        # 同步更新User表中的数据
        user = UserModel.objects.get(username=instance.username)
        user.email = instance.email
        user.username = instance.username
        user.tel = instance.phone
        user.save()

        instance.save()
        return instance


class StudentNotMeSerializer(serializers.ModelSerializer):

    college = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'username',
            'gender', 'prize_num', 'race_num', 'college_id', 'avatar', 'college', 'note'
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


class StudentAvatarSerializer(serializers.ModelSerializer):

    avatar = serializers.FileField(required=True)

    class Meta:
        model = Student
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
