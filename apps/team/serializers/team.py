from django.db import transaction
from apps.student.models import Student
from apps.teacher.models import Teacher
from apps.team.models import StudentToTeam, TeacherToTeam
from .baseSerializers import *


class TeamUpdateSerializer(BaseTeamSerializer):
    """团队更新序列化器"""
    class Meta(BaseTeamSerializer.Meta):
        fields = ['name']  # 只允许修改团队名称
        extra_kwargs = {
            'name': {'required': False, 'min_length': 2}
        }


class TeamMemberInviteSerializer(BaseInviteSerializer):
    """团队成员邀请序列化器"""
    target_sn = serializers.CharField(required=True, help_text="新成员的SN")

    def get_target_field(self):
        return 'student'

    def get_invite_model(self):
        return StudentToTeam

    def get_target_model(self):
        return Student

    def validate(self, attrs):
        team_sn = self.validate_team(attrs['team_sn'])
        member_sn = self.validate_target(Student, 'sn', attrs['target_sn'], "成员不存在")
        self.validate_invite_exists(StudentToTeam, team_sn, member_sn, "该成员已被邀请")
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            return self.create_invite(
                validated_data['team_sn'],
                validated_data['target_sn'],
                is_cap=False
            )


class TeamTeacherInviteSerializer(BaseInviteSerializer):
    """团队老师邀请序列化器"""
    target_sn = serializers.CharField(required=True, help_text="新老师的SN")

    def get_target_field(self):
        return 'teacher'

    def get_invite_model(self):
        return TeacherToTeam

    def get_target_model(self):
        return Teacher

    def validate(self, attrs):
        team_sn = self.validate_team(attrs['team_sn'])
        teacher_sn = self.validate_target(Teacher, 'sn', attrs['target_sn'], "老师不存在")
        self.validate_invite_exists(TeacherToTeam, team_sn, teacher_sn, "该老师已被邀请")
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            return self.create_invite(
                validated_data['team_sn'],
                validated_data['target_sn']
            )


class TeamStudentConfirmSerializer(BaseConfirmSerializer):
    """学生确认序列化器"""
    class Meta(BaseConfirmSerializer.Meta):
        model = StudentToTeam

    def validate(self, attrs):
        self.validate_user_permission(self.context['request'], 'student', 'sn')
        return attrs


class TeamTeacherConfirmSerializer(BaseConfirmSerializer):
    """老师确认序列化器"""
    class Meta(BaseConfirmSerializer.Meta):
        model = TeacherToTeam

    def validate(self, attrs):
        self.validate_user_permission(self.context['request'], 'teacher', 'sn')
        return attrs


class TeamCreateSerializer(serializers.ModelSerializer):
    """团队创建序列化器"""
    member_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        default=[]
    )
    teacher_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="老师的用户SN"
    )

    class Meta:
        model = Team
        fields = ['name', 'member_ids', 'teacher_ids']
        read_only_fields = ['id', 'sn']

    def validate_ids(self, ids, model, sn_field='sn', error_msg="不存在"):
        """验证ID列表"""
        invalid_ids = [
            id for id in ids
            if not model.objects.filter(**{sn_field: id}).exists()
        ]
        if invalid_ids:
            raise ValidationError(f"以下{error_msg}: {', '.join(invalid_ids)}")
        return ids

    def validate(self, attrs):
        # 验证队长
        if not Student.objects.filter(id=self.context['request'].id).exists():
            raise ValidationError("队长用户不存在")

        # 验证成员
        self.validate_ids(attrs.get('member_ids', []), Student, error_msg="成员ID不存在")

        # 验证老师
        self.validate_ids(attrs.get('teacher_ids', []), Teacher, error_msg="老师ID不存在")

        return attrs

    def create_team_member(self, team_sn, student_sn, is_cap=False, status='confirmed'):
        """创建团队成员"""
        return StudentToTeam.objects.create(
            team=team_sn,
            student=student_sn,
            is_cap=is_cap,
            status=status
        )

    def create_team_teacher(self, team_sn, teacher_sn, status='pending'):
        """创建团队老师"""
        return TeacherToTeam.objects.create(
            team=team_sn,
            teacher=teacher_sn,
            status=status
        )

    def create(self, validated_data):
        with transaction.atomic():
            team = Team.objects.create(
                name=validated_data['name'],
                cap=self.context['request'].sn,
                people_num=0,
                state=0,
            )

            # 添加队长
            self.create_team_member(team.sn, self.context['request'].sn, is_cap=True)

            # 添加成员
            for member_id in validated_data.get('member_ids', []):
                self.create_team_member(team.sn, member_id, status='pending')

            # 添加老师
            for teacher_id in validated_data.get('teacher_ids', []):
                self.create_team_teacher(team.sn, teacher_id)

            return team