from apps.team.models import Team
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['create_time','id','sn', 'name', 'cap', 'people_num', 'race_num', 'prize_num', 'teacher_num']
        extra_kwargs = {
            'sn': {'read_only': True},
            'cap': {'read_only': True},
        }

class AllTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['create_time','id','sn', 'name', 'cap', 'people_num', 'race_num', 'prize_num', 'teacher_num']
        extra_kwargs = {
            'sn': {'read_only': True},
        }

class TeamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name']  # 只允许修改团队名称（可根据需求添加其他可修改字段）
        extra_kwargs = {
            'name': {'required': False}  # 使字段可选
        }

    def validate(self, attrs):
        # 可以在这里添加额外的验证逻辑
        if 'name' in attrs and len(attrs['name']) < 2:
            raise ValidationError("团队名称至少需要2个字符")
        return attrs