# serializers.py
from rest_framework import serializers
from apps.teacher.models import Teacher


class TeacherListSerializer(serializers.ModelSerializer):
    college = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['id', 'username', 'sn', 'college', 'phone', 'avatar']
        read_only_fields = fields  # 所有字段均为只读

    def get_college(self, obj):
        """处理学院信息的序列化"""
        return obj.get_college(obj.college_id)