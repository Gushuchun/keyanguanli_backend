from django.template.context_processors import request
from rest_framework import serializers
from django.db import transaction
from apps.team.models import Team, TeamInvite
from apps.team.models import StudentToTeam, TeacherToTeam
from apps.student.models import Student
from apps.teacher.models import Teacher
from django.db.models import F

class TeamInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamInvite
        fields = ['id', 'sn', 'team', 'member_id', 'cap', 'teacher', 'status']
        read_only_fields = ['id', 'sn', 'cap']


class TeamCreateSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        default=[]
    )
    teacher_id = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="老师的用户ID"
    )

    class Meta:
        model = Team
        fields = ['name', 'member_ids', 'teacher_id']
        read_only_fields = ['id', 'sn']

    def validate(self, attrs):
        member_ids = attrs.get('member_ids', [])
        teacher_id = attrs.get('teacher_id')
        captain_id = self.context['request'].id

        if not Student.objects.filter(id=captain_id).exists():
            raise serializers.ValidationError("队长用户不存在")

        for member_id in member_ids:
            if not Student.objects.filter(sn=member_id).exists():
                raise serializers.ValidationError(f"成员ID {member_id} 不存在")

        if teacher_id and not Teacher.objects.filter(sn=teacher_id).exists():
            raise serializers.ValidationError("指定的老师不存在")

        return attrs

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        teacher_ids = validated_data.pop('teacher_id', [])
        captain_sn = self.context['request'].sn

        # teacher_id = Teacher.objects.filter(sn=teacher_id).first().sn

        with transaction.atomic():
            # 创建团队，初始状态为0(未激活)
            team = Team.objects.create(
                name=validated_data['name'],
                cap=captain_sn,
                people_num=0,  # 初始为0，激活时再计算
                state=0,  # 0=未激活，1=已激活
            )

            # 自动将队长添加到学生-团队关联表
            StudentToTeam.objects.create(
                student=captain_sn,
                team=team.sn,
                state=0,
                is_cap=True
            )

            invites = []
            # 创建成员邀请
            for member_id in member_ids:
                invites.append(TeamInvite(
                    team=team.id,
                    member_id=member_id,
                    cap=captain_sn,
                    status='0'
                ))

            # 创建老师邀请（如果有老师）
            for teacher_id in teacher_ids:
                invites.append(TeamInvite(
                    team=team.id,
                    teacher=teacher_id,
                    cap=captain_sn,
                    status='0'
                ))

            if invites:
                TeamInvite.objects.bulk_create(invites)

            return team


class TeamConfirmSerializer(serializers.Serializer):
    team = serializers.CharField(required=True, help_text="团队ID")
    status = serializers.ChoiceField(
        choices=['1', '2'],
        required=True,
        help_text="邀请状态: 1(接受)2(拒绝)"
    )

    def validate(self, attrs):
        team_id = attrs['team']
        user_id = self.context['request'].sn
        role = self.context['request'].role

        # 检查是否存在该用户的待处理邀请
        if role =='student':
            if not TeamInvite.objects.filter(
                    team=team_id,
                    member_id=user_id,
                    status='0'  # 只处理待处理的邀请
            ).exists():
                raise serializers.ValidationError("没有找到您的待处理邀请，或邀请已被处理")
        elif role == 'teacher':
            if not TeamInvite.objects.filter(
                    team=team_id,
                    teacher=user_id,
                    status='0'  # 只处理待处理的邀请
            ).exists():
                raise serializers.ValidationError("没有找到您的待处理邀请，或邀请已被处理")

        return attrs

    def update(self, instance, validated_data):
        team_id = validated_data['team']
        status = validated_data['status']
        user_id = self.context['request'].sn
        user = self.context['request'].user  # 获取当前用户对象
        role = self.context['request'].user.role  # 获取当前用户的角色

        team_sn = Team.objects.get(id=team_id).sn

        with transaction.atomic():
            # 获取并更新邀请状态
            if role == 'student':
                invite = TeamInvite.objects.get(
                    team=team_id,
                    member_id=user_id,
                    status='0'
                )
            elif role =='teacher':
                invite = TeamInvite.objects.get(
                    team=team_id,
                    teacher=user_id,
                    status='0'
                )
            invite.status = status
            invite.save()

            # 如果是接受邀请，创建关联记录
            if status == '1':
                # 检查用户是学生还是老师
                # 是学生
                if role == 'student':
                    StudentToTeam.objects.create(
                        student=user_id,
                        team=team_sn,
                        state=1,
                    )
                elif role == 'teacher':
                    TeacherToTeam.objects.create(
                        teacher=user_id,
                        team=team_sn,
                        state=1,
                    )
                    team = Team.objects.filter(id=team_id)
                    if team.exists():
                        team.update(teacher_num=F('teacher_num') + 1)
                    else:
                        raise ValueError(f"团队 ID {team_id} 不存在")
                else:
                    raise serializers.ValidationError("用户既不是学生也不是老师")

            # 获取团队和所有邀请
            team = Team.objects.get(id=team_id)
            all_invites = TeamInvite.objects.filter(team=team_id)

            # 检查是否所有邀请都已处理
            pending_invites = all_invites.filter(status='0').exists()

            if not pending_invites:
                # 所有邀请都已处理
                accepted_invites = all_invites.filter(status='1')

                if accepted_invites.exists():
                    # 有成员接受邀请，激活团队
                    team.state = 1  # 激活状态

                    # 更新所有接受成员的状态为1(已确认)
                    StudentToTeam.objects.filter(team=team_sn).update(state=1)
                    TeacherToTeam.objects.filter(team=team_sn).update(state=1)

                    # 计算团队成员数（学生+老师+队长）
                    student_count = StudentToTeam.objects.filter(team=team_sn).count()
                    teacher_count = TeacherToTeam.objects.filter(team=team_sn).count()
                    team.people_num = student_count + teacher_count  # +1 是队长

                    team.save()


                    return {
                        'team': team,
                        'activated': True,
                        'message': '团队已成功激活'
                    }
                else:
                    # 所有人都拒绝了，创建失败，
                    StudentToTeam.objects.filter(team=team_sn).update(state=0)
                    TeacherToTeam.objects.filter(team=team_sn).update(state=0)

                    return {
                        'team': None,
                        'activated': False,
                        'message': '所有邀请被拒绝，团队已删除'
                    }

            # 还有未处理的邀请
            return {
                'team': team,
                'activated': False,
                'message': '等待其他成员确认'
            }


class TeamInviteNewMemberSerializer(serializers.Serializer):
    team_id = serializers.CharField(required=True, help_text="团队ID")
    member_sn = serializers.CharField(required=True, help_text="新成员的SN")

    def validate(self, attrs):
        team_id = attrs['team_id']
        member_sn = attrs['member_sn']

        # 检查团队是否存在
        if not Team.objects.filter(id=team_id).exists():
            raise serializers.ValidationError("团队不存在")

        # 检查成员是否存在
        if not Student.objects.filter(sn=member_sn).exists():
            raise serializers.ValidationError("成员不存在")

        # 检查是否已经邀请过该成员
        if TeamInvite.objects.filter(team=team_id, member_id=member_sn, status='0').exists():
            raise serializers.ValidationError("该成员已被邀请")

        return attrs

    def create(self, validated_data):
        team_id = validated_data['team_id']
        member_sn = validated_data['member_sn']
        captain_sn = self.context['request'].sn

        with transaction.atomic():
            # 创建邀请记录
            invite = TeamInvite.objects.create(
                team=team_id,
                member_id=member_sn,
                cap=captain_sn,
                status='0'  # 0=待接受
            )

            return invite


class TeamInviteNewTeacherSerializer(serializers.Serializer):
    team_id = serializers.CharField(required=True, help_text="团队ID")
    teacher_sn = serializers.CharField(required=True, help_text="新老师的SN")

    def validate(self, attrs):
        team_id = attrs['team_id']
        teacher_sn = attrs['teacher_sn']

        # 检查团队是否存在
        if not Team.objects.filter(id=team_id).exists():
            raise serializers.ValidationError("团队不存在")

        # 检查老师是否存在
        if not Teacher.objects.filter(sn=teacher_sn).exists():
            raise serializers.ValidationError("老师不存在")

        # 检查是否已经邀请过该老师
        if TeamInvite.objects.filter(team=team_id, teacher=teacher_sn, status='0').exists():
            raise serializers.ValidationError("该老师已被邀请")

        return attrs

    def create(self, validated_data):
        team_id = validated_data['team_id']
        teacher_sn = validated_data['teacher_sn']
        captain_sn = self.context['request'].sn

        with transaction.atomic():
            # 创建邀请记录
            invite = TeamInvite.objects.create(
                team=team_id,
                teacher=teacher_sn,
                cap=captain_sn,
                status='0'  # 0=待接受
            )

            return invite
