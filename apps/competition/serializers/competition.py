from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _
from apps.competition.models import Competition, StudentToCompetition, TeacherToCompetition
from apps.team.models import Team, StudentToTeam
from .BaseSerializers import *


class CompetitionCreateSerializer(BaseCompetitionSerializer):
    """竞赛创建序列化器"""
    teacher_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        default=[]
    )

    class Meta(BaseCompetitionSerializer.Meta):
        fields = BaseCompetitionSerializer.Meta.fields + ['teacher_ids']
        extra_kwargs = {
            **BaseCompetitionSerializer.Meta.extra_kwargs,
            'team_id': {'required': True},
            'certificate_image': {'required': True}
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        self.validate_team_permission(attrs['team_id'], self.context['request'])

        if Competition.objects.filter(team_id=attrs['team_id'], title=attrs['title']).exists():
            raise ValidationError("该团队已存在同名比赛，请更换比赛名称")

        return attrs

    def create_confirm_records(self, competition, team_id, teacher_ids):
        """创建确认记录"""
        # 为学生创建确认记录
        team_members = StudentToTeam.objects.filter(team=team_id)
        for member in team_members:
            StudentToCompetition.objects.create(
                competition=competition.sn,
                student=member.student,
                status='confirmed' if member.is_cap else 'pending',
                is_cap=member.is_cap,
                team=team_id
            )

        # 为老师创建确认记录
        for teacher_id in teacher_ids:
            TeacherToCompetition.objects.create(
                competition=competition.sn,
                teacher=teacher_id,
                status='pending',
                team=team_id
            )

    def create(self, validated_data):
        teacher_ids = validated_data.pop('teacher_ids', [])
        image_files = validated_data.pop('certificate_image')

        with transaction.atomic():
            file_url = self.handle_image_upload(image_files)
            competition = Competition.objects.create(
                **validated_data,
                file=file_url,
                status='pending'
            )

            self.create_confirm_records(competition, validated_data['team_id'], teacher_ids)
            return competition


class CompetitionUpdateSerializer(BaseCompetitionSerializer):
    """竞赛更新序列化器"""
    teacher_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        default=[]
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance.status == 'confirmed':
            raise ValidationError(_("比赛已确认，不能再修改"))
        return attrs

    def update(self, instance, validated_data):
        teacher_ids = validated_data.pop('teacher_ids', [])
        image_files = validated_data.pop('certificate_image', None)

        with transaction.atomic():
            if image_files:
                validated_data['file'] = self.handle_image_upload(image_files, instance)

            for field, value in validated_data.items():
                setattr(instance, field, value)

            # 添加新老师
            for teacher_id in teacher_ids:
                TeacherToCompetition.objects.get_or_create(
                    competition=instance.sn,
                    teacher=teacher_id,
                    defaults={'status': 'pending', 'team': instance.team_id}
                )
                instance.teacher_num += 1

            instance.save()
            return instance


class CompetitionMemberConfirmSerializer(BaseConfirmSerializer):
    """成员确认序列化器"""

    class Meta:
        model = StudentToCompetition
        fields = ['sn', 'student', 'status', 'note']
        extra_kwargs = {
            'sn': {'read_only': True},
            'student': {'read_only': True},
        }

    def validate(self, attrs):
        self.validate_user_permission(self.context['request'], 'student')
        return attrs


class CompetitionTeacherConfirmSerializer(BaseConfirmSerializer):
    """老师确认序列化器"""

    class Meta:
        model = TeacherToCompetition
        fields = ['sn', 'status', 'note', 'teacher']
        extra_kwargs = {
            'sn': {'read_only': True},
            'teacher': {'read_only': True},
        }

    def validate(self, attrs):
        self.validate_user_permission(self.context['request'], 'teacher')
        return attrs