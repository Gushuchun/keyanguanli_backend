from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from apps.competition.models import Competition
from apps.team.models import Team
from utils.service.minio_utils import upload_competition_image_to_minio, delete_files_from_minio


class BaseCompetitionSerializer(serializers.ModelSerializer):
    """竞赛基础序列化器"""
    certificate_image = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="证书图片文件列表（JPEG/PNG，最大5MB）"
    )

    class Meta:
        model = Competition
        fields = ['sn', 'date', 'description', 'score', 'team_sn', 'file',
                  'note', 'title', 'certificate_image', 'status', 'id',]
        extra_kwargs = {
            'sn': {'read_only': True},
            'status': {'read_only': True},
            'file': {'read_only': True}
        }

    def validate_team_permission(self, team_id, request):
        """验证团队权限"""
        try:
            team = Team.objects.get(sn=team_id)
            if team.cap != request.sn:
                raise PermissionDenied("只有队长可以操作比赛信息")
            return team
        except Team.DoesNotExist:
            raise ValidationError("团队不存在")

    def handle_image_upload(self, image_files, instance=None):
        """处理图片上传"""
        if not image_files:
            return None

        if instance and instance.file:
            delete_files_from_minio(instance.file)

        image_urls = upload_competition_image_to_minio(image_files)
        return ",".join(image_urls)


class BaseConfirmSerializer(serializers.ModelSerializer):
    """确认基础序列化器"""

    def validate_status(self, value):
        if value not in ['confirmed', 'rejected']:
            raise ValidationError("状态只能更新为 'confirmed' 或 'rejected'")
        return value

    def validate_user_permission(self, request, field_name):
        """验证用户权限"""
        if getattr(request, 'sn') != getattr(self.instance, field_name):
            raise PermissionDenied("只能确认自己的参赛记录")


class BaseInviteSerializer(serializers.Serializer):
    """邀请基础序列化器"""
    competition_sn = serializers.CharField(required=True)
    target_sn = serializers.CharField(required=True)

    def validate_competition(self, competition_sn):
        """验证团队是否存在"""
        if not Competition.objects.filter(sn=competition_sn).exists():
            raise ValidationError("比赛不存在")
        return competition_sn

    def validate_target(self, model, sn_field, sn, error_msg):
        """验证目标(成员/老师)是否存在"""
        if not model.objects.filter(**{sn_field: sn}).exists():
            raise ValidationError(error_msg)
        return sn

    def validate_invite_exists(self, model, competition_sn, target_sn, error_msg):
        """验证是否已邀请(排除已拒绝的)"""
        if model.objects.filter(competition=competition_sn, state=1, **{self.get_target_field(): target_sn}).exclude(status='rejected').exists():
            raise ValidationError(error_msg)
        return True

    def get_target_field(self):
        """获取目标字段名(子类实现)"""
        raise NotImplementedError

    def get_invite_model(self):
        """获取邀请模型(子类实现)"""
        raise NotImplementedError

    def get_target_model(self):
        """获取目标模型(子类实现)"""
        raise NotImplementedError

    def create_invite(self, competition_sn, target_sn, **extra_fields):
        """创建邀请记录"""
        return self.get_invite_model().objects.create(
            competition=competition_sn,
            **{self.get_target_field(): target_sn},
            status='pending',
            **extra_fields
        )
