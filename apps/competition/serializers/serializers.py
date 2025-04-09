from rest_framework import serializers
from rest_framework.response import Response

from apps.competition.models import Competition, CompetitionMemberConfirm
from apps.team.models import StudentToTeam, Team
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _

from utils.minio_utils import upload_competition_image_to_minio, delete_files_from_minio


class CompetitionSerializer(serializers.ModelSerializer):
    note = serializers.CharField(required=False, allow_blank=True)
    certificate_image = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True,
        help_text="证书图片文件列表（JPEG/PNG，最大5MB）"
    )
    teacher_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        default=[]
    )

    class Meta:
        model = Competition
        fields = [
            'sn', 'date', 'description', 'score', 'team_id',
            'file', 'note', 'title', 'teacher_ids', 'certificate_image'
        ]
        extra_kwargs = {
            'sn': {'read_only': True},
            'status': {'read_only': True},
            'team_id': {'required': True},
            'file': {'read_only': True}  # 文件URL由系统生成
        }

    def validate(self, attrs):
        # 获取当前用户
        sn = self.context['request'].sn
        team_id = attrs.get('team_id')
        title = attrs.get('title')

        # 检查用户是否是队长
        try:
            team = Team.objects.get(sn=team_id)
            if team.cap != sn:
                raise ValidationError("只有队长可以创建比赛信息")
        except Team.DoesNotExist:
            raise ValidationError("团队不存在")

        # 验证图片文件（自动触发ImageField验证）
        if 'certificate_image' not in attrs:
            raise serializers.ValidationError({"certificate_image": "必须上传证书图片"})

        if Competition.objects.filter(team_id=team_id, title=title).exists():
            raise ValidationError("该团队已存在同名比赛，请更换比赛名称")

        return attrs

    def create(self, validated_data):
        teacher_ids = validated_data.pop('teacher_ids', [])
        image_files = validated_data.pop('certificate_image')  # 多张图片

        with transaction.atomic():
            # 创建比赛记录
            image_urls = upload_competition_image_to_minio(image_files)  # 上传多个图片
            file_urls = ",".join(image_urls)
            print(len(file_urls))
            competition = Competition.objects.create(
                **validated_data,
                file=file_urls,  # 用逗号分隔多个文件的 URL
                status='pending'
            )

            # 为每个团队成员创建确认记录
            team_members = StudentToTeam.objects.filter(team=validated_data['team_id'])
            for member in team_members:
                if member.is_cap == False:
                    CompetitionMemberConfirm.objects.create(
                        sn=competition.sn,
                        student=member.student,
                        status='pending',
                        is_cap=False
                    )
                else:
                    CompetitionMemberConfirm.objects.create(
                        sn=competition.sn,
                        student=member.student,
                        status='confirmed',
                        is_cap=True
                    )

            for teacher_id in teacher_ids:
                CompetitionMemberConfirm.objects.create(
                    sn=competition.sn,
                    teacher=teacher_id,
                    status='pending'
                )

            return competition



class CompetitionMemberConfirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionMemberConfirm
        fields = ['sn', 'student', 'status', 'note', 'teacher']
        extra_kwargs = {
            'sn': {'read_only': True},
            'student': {'read_only': True},
            'teacher': {'read_only': True},
        }

    def validate_status(self, value):
        if value != 'confirmed' and value is not None:
            raise serializers.ValidationError("状态只能更新为 'confirmed'")
        return value

    def validate(self, attrs):
        # 确保请求用户是记录对应的用户
        if str(self.context['request'].sn) != str(self.instance.student) and \
                str(self.context['request'].sn) != str(self.instance.teacher):
            raise PermissionDenied("只能确认自己的参赛记录或作为带队老师确认")
        return attrs


class CompetitionUpdateSerializer(serializers.ModelSerializer):
    certificate_image = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True,
        help_text="证书图片文件列表（JPEG/PNG，最大5MB）"
    )

    class Meta:
        model = Competition
        fields = [
            'id', 'note', 'date', 'title', 'description',
            'teacher_num', 'file', 'score', 'status', 'certificate_image'
        ]
        read_only_fields = ['id', 'status', 'teacher_num']  # status 禁止直接修改

    def validate(self, attrs):
        instance = self.instance

        # 仅当是更新时校验状态
        if instance and instance.status == 'confirmed':
            raise serializers.ValidationError(_("比赛已确认，不能再修改"))

        if 'certificate_image' not in attrs:
            raise serializers.ValidationError({"certificate_image": "必须上传证书图片"})

        return attrs

    def update(self, instance, validated_data):
        teacher_ids = validated_data.pop('teacher_ids', [])
        image_files = validated_data.pop('certificate_image', None)

        # 如果有新的图片上传，删除旧的图片
        if image_files:
            old_file_urls = instance.file

            # 上传新图片并获取 URL 列表
            image_urls = upload_competition_image_to_minio(image_files)
            if old_file_urls:
                delete_files_from_minio(old_file_urls)

            file_urls = ",".join(image_urls)
            validated_data['file'] = file_urls  # 更新比赛记录中的文件字段

        # 更新比赛记录
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        # 更新老师确认记录
        CompetitionMemberConfirm.objects.filter(sn=instance.sn).delete()
        for teacher_id in teacher_ids:
            CompetitionMemberConfirm.objects.create(
                sn=instance.sn,
                teacher=teacher_id,
                status='pending'
            )

        return instance