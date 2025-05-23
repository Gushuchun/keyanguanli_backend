from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from apps.team.models import Team, StudentToTeam, TeacherToTeam
from apps.student.models import Student
from apps.teacher.models import Teacher
from apps.competition.models import Competition
from .baseSerializers import *
from apps.settings.models import UserSettings

class TeamDetailSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    competitions = serializers.SerializerMethodField()
    cap_name = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'create_time', 'id', 'sn', 'name', 'cap', 'people_num', 'race_num', 
            'prize_num', 'teacher_num', 'students', 'teachers', 'competitions', 'cap_name', 'status'
        ]

    def get_cap_name(self, obj):
        cap = Student.objects.get(sn=obj.cap)
        return cap.username

    def get_students(self, obj):
        students = StudentToTeam.objects.filter(team=obj.sn, status='confirmed', state=1)
        students_info = []
        for student in students:
            student_info = Student.objects.get(sn=student.student)
            students_info.append({
                'name': student_info.username,
                'college': student_info.get_college(student_info.college_id),
                'phone': student_info.phone,
                'email': student_info.email,
                'avatar': student_info.avatar if student_info.avatar else None,
                'join_time': student.create_time,
                'sn': student_info.sn,
                'status': student.status,
            })
        return students_info

    def get_teachers(self, obj):
        teachers = TeacherToTeam.objects.filter(team=obj.sn, status='confirmed', state=1)
        teachers_info = []
        for teacher in teachers:
            teacher_info = Teacher.objects.get(sn=teacher.teacher)
            teachers_info.append({
                'name': teacher_info.username,
                'college': teacher_info.get_college(teacher_info.college_id),
                'phone': teacher_info.phone,
                'email': teacher_info.email,
                'avatar': teacher_info.avatar if teacher_info.avatar else None,
                'join_time': teacher.create_time,
                'sn': teacher_info.sn,
                'status': teacher.status,
            })
        return teachers_info

    def get_competitions(self, obj):
        competitions = Competition.objects.filter(team_sn=obj.sn, state=1, status='confirmed')
        competitions_info = []
        for competition in competitions:
            competitions_info.append({
                'title': competition.title,
                'date': competition.date,
                'description': competition.description,
                'score': competition.score,
                'award_time': competition.create_time,
                'id': competition.id,
            })
        return competitions_info


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
            invite = self.create_invite(
                validated_data['team_sn'],
                validated_data['target_sn']
            )

            # 获取团队和被邀请人信息
            team = Team.objects.get(sn=validated_data['team_sn'])
            student = Student.objects.get(sn=validated_data['target_sn'])

            captain = Student.objects.get(id=self.context['request'].id)
            is_send = UserSettings.objects.get(sn=captain.sn, state=1).send_email

            if is_send:
                # 发送邮件
                subject = f"科研管理平台 邀请加入团队"
                message = (
                    f" {student.username}您好，您已被邀请加入团队 \"{team.name}\"。请登录科研管理平台查看邀请并确认。\n\n"
                )
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [student.email]
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return invite


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
            invite = self.create_invite(
                validated_data['team_sn'],
                validated_data['target_sn']
            )

            # 获取团队和被邀请人信息
            team = Team.objects.get(sn=validated_data['team_sn'])
            student = Student.objects.get(sn=validated_data['target_sn'])

            captain = Teacher.objects.get(id=self.context['request'].id)
            is_send = UserSettings.objects.get(sn=captain.sn, state=1).send_email

            if is_send:
                # 发送邮件
                subject = f"科研管理平台 邀请加入团队"
                message = (
                    f"{student.username}您好，您已被邀请加入团队 \"{team.name}\"。请登录科研管理平台查看邀请并确认。\n\n"
                )
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [student.email]
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return invite


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

        # 验证团队名是否已存在
        if Team.objects.filter(name=attrs['name'], state=1).exists():
            raise ValidationError("团队名已存在")

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
            # 创建团队
            team = Team.objects.create(
                name=validated_data['name'],
                cap=self.context['request'].sn,
                people_num=1,
                state=1,
                status='pending'
            )

            # 添加队长为团队成员
            captain = Student.objects.get(id=self.context['request'].id)
            self.create_team_member(team.sn, self.context['request'].sn, is_cap=True)

            is_send = UserSettings.objects.get(sn=captain.sn, state=1).send_email

            # 收集被邀请成员的邮箱
            invited_emails = []

            # 添加其他成员
            for member_id in validated_data.get('member_ids', []):
                student = Student.objects.get(sn=member_id)
                self.create_team_member(team.sn, member_id, status='pending')
                invited_emails.append(student.email)  # 收集成员邮箱

            # 添加老师
            for teacher_id in validated_data.get('teacher_ids', []):
                self.create_team_teacher(team.sn, teacher_id)
                teacher = Teacher.objects.get(sn=teacher_id)
                invited_emails.append(teacher.email)  # 收集老师邮箱

            # 发送邮件给所有非队长成员
            if invited_emails and is_send:
                subject = f"科研管理平台 新建团队邀请"
                message = (
                    f"您好，您已被邀请加入团队 \"{team.name}\"，请登录科研管理平台查看邀请并确认.\n"
                )
                from_email = settings.DEFAULT_FROM_EMAIL
                send_mail(subject, message, from_email, invited_emails, fail_silently=False)

            return team

