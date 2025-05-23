from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _
from apps.competition.models import Competition, StudentToCompetition, TeacherToCompetition
from apps.team.models import Team, StudentToTeam
from .BaseSerializers import *
from ...teacher.models import Teacher
from .BaseSerializers import BaseInviteSerializer


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
            'team_sn': {'required': True},
            'certificate_image': {'required': True}
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        self.validate_team_permission(attrs['team_sn'], self.context['request'])

        if Competition.objects.filter(team_sn=attrs['team_sn'], title=attrs['title']).exists():
            raise ValidationError("该团队已存在同名比赛，请更换比赛名称")

        return attrs

    def create_confirm_records(self, competition, team_sn, teacher_ids):
        """创建确认记录"""
        # 为学生创建确认记录
        team_members = StudentToTeam.objects.filter(team=team_sn)
        for member in team_members:
            StudentToCompetition.objects.create(
                competition=competition.sn,
                student=member.student,
                status='confirmed' if member.is_cap else 'pending',
                is_cap=member.is_cap,
                team=team_sn
            )

        # 为老师创建确认记录
        for teacher_id in teacher_ids:
            TeacherToCompetition.objects.create(
                competition=competition.sn,
                teacher=teacher_id,
                status='pending',
                team=team_sn
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

            self.create_confirm_records(competition, validated_data['team_sn'], teacher_ids)
            return competition


class CompetitionUpdateSerializer(BaseCompetitionSerializer):
    """竞赛更新序列化器"""

    class Meta(BaseCompetitionSerializer.Meta):
        extra_kwargs = {
            **BaseCompetitionSerializer.Meta.extra_kwargs,
            'score': {'required': False}  # 将 score 字段设置为可选
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance.status == 'confirmed':
            raise ValidationError(_("比赛已确认，不能再修改"))
        return attrs

    def update(self, instance, validated_data):
        image_files = validated_data.pop('certificate_image', None)

        with transaction.atomic():
            if image_files:
                validated_data['file'] = self.handle_image_upload(image_files, instance)

            for field, value in validated_data.items():
                setattr(instance, field, value)

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


class CompetitionDetailSerializer(BaseCompetitionSerializer):
    team_id = serializers.SerializerMethodField()
    teachers_info = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    captain_id = serializers.SerializerMethodField()

    class Meta(BaseCompetitionSerializer.Meta):
        fields = BaseCompetitionSerializer.Meta.fields + ['team_id', 'teachers_info', 'team_name', 'captain_id']

    def get_captain_id(self, obj):
        team = Team.objects.filter(sn=obj.team_sn).first()
        if team:
            captain = StudentToTeam.objects.filter(team=team.sn, is_cap=True, state=1).first()
            if captain:
                return captain.student

    def get_team_name(self, obj):
        team = Team.objects.filter(sn=obj.team_sn, state=1).first()
        if team:
            return team.name
        return None

    def get_team_id(self, obj):
        team = Team.objects.filter(sn=obj.team_sn, state=1).first()
        if team:
            return team.id
        return None

    def get_teachers_info(self, obj):
        teachers = TeacherToCompetition.objects.filter(competition=obj.sn, state=1, status='confirmed')
        teachers_info = []
        for teacher in teachers:
            teacher_info = Teacher.objects.filter(sn=teacher.teacher, state=1).first()
            if teacher_info:
                teachers_info.append({
                    'id': teacher_info.id,
                    'sn': teacher_info.sn,
                    'avatar': teacher_info.avatar if teacher_info.avatar else None,
                    'name': teacher_info.username,
                })
        return teachers_info


class CompetitionTeacherInviteSerializer(BaseInviteSerializer):
    """竞赛老师邀请序列化器"""
    target_sn = serializers.CharField(required=True, help_text="新老师的SN")

    def get_target_field(self):
        return 'teacher'

    def get_invite_model(self):
        return TeacherToCompetition

    def get_target_model(self):
        return Teacher

    def validate(self, attrs):
        competition_sn = self.validate_competition(attrs['competition_sn'])
        teacher_sn = self.validate_target(Teacher, 'sn', attrs['target_sn'], "老师不存在")
        self.validate_invite_exists(TeacherToCompetition, competition_sn, teacher_sn, "该老师已被邀请")
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            return self.create_invite(
                validated_data['competition_sn'],
                validated_data['target_sn'],
            )
