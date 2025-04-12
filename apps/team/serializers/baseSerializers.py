from apps.team.models import Team
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

class BaseTeamSerializer(serializers.ModelSerializer):
    """团队基础序列化器"""
    class Meta:
        model = Team
        fields = ['create_time', 'id', 'sn', 'name', 'cap', 'people_num', 'race_num', 'prize_num', 'teacher_num']
        extra_kwargs = {
            'sn': {'read_only': True},
            'cap': {'read_only': True},
        }


class BaseInviteSerializer(serializers.Serializer):
    """邀请基础序列化器"""
    team_sn = serializers.CharField(required=True)
    target_sn = serializers.CharField(required=True)

    def validate_team(self, team_sn):
        """验证团队是否存在"""
        if not Team.objects.filter(sn=team_sn).exists():
            raise ValidationError("团队不存在")
        return team_sn

    def validate_target(self, model, sn_field, sn, error_msg):
        """验证目标(成员/老师)是否存在"""
        if not model.objects.filter(**{sn_field: sn}).exists():
            raise ValidationError(error_msg)
        return sn

    def validate_invite_exists(self, model, team_sn, target_sn, error_msg):
        """验证是否已邀请(排除已拒绝的)"""
        if model.objects.filter(team=team_sn, **{self.get_target_field(): target_sn}).exclude(status='rejected').exists():
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

    def create_invite(self, team_sn, target_sn, **extra_fields):
        """创建邀请记录"""
        return self.get_invite_model().objects.create(
            team=team_sn,
            **{self.get_target_field(): target_sn},
            status='pending',
            **extra_fields
        )


class BaseConfirmSerializer(serializers.ModelSerializer):
    """确认基础序列化器"""
    class Meta:
        fields = ['status']
        extra_kwargs = {
            'status': {'required': True}
        }

    def validate_status(self, value):
        if value not in ['confirmed', 'rejected']:
            raise ValidationError("状态只能更新为 'confirmed' 或 'rejected'")
        return value

    def validate_user_permission(self, request, instance_field, user_field):
        if getattr(request, user_field) != getattr(self.instance, instance_field):
            raise PermissionDenied(f"只能确认自己的记录")
        return True