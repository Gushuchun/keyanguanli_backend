from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.student.models import Student
from apps.teacher.models import Teacher
from django.db import transaction

User = get_user_model()

class BaseRegistrationSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['student', 'teacher'], write_only=True)
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True, min_length=6)
    college_id = serializers.IntegerField()
    phone = serializers.CharField(max_length=20)
    email = serializers.CharField(required=False, allow_blank=True, max_length=100)
    gender = serializers.ChoiceField(choices=[(True, '男'), (False, '女')], required=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        email = validated_data['email']


        with transaction.atomic():
            # 创建用户
            user = User.objects.create_user(
                username=validated_data['username'],
                password=password,
                email=email,
                role=role,
            )

            # 创建对应角色
            if role == 'teacher':
                return self.create_teacher(user, validated_data)
            return self.create_student(user, validated_data)



class StudentRegistrationSerializer(BaseRegistrationSerializer):
    cn = serializers.CharField(max_length=100)
    team_id = serializers.CharField(required=False, allow_blank=True)

    def create_student(self, user, validated_data):
        with transaction.atomic():
            # 创建学生
            student = Student.objects.create(
                **validated_data
            )
            student.set_cn(validated_data['cn'])
            # 返回学生对象
            return student

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # 解密身份证号
        representation['cn'] = instance.get_cn()
        representation['gender'] = '1' if instance.gender else '0'
        return representation


class TeacherRegistrationSerializer(BaseRegistrationSerializer):
    email = serializers.EmailField()
    # title = serializers.CharField(default='assistant')

    def create_teacher(self, user, validated_data):
        with transaction.atomic():
            # 创建教师
            teacher = Teacher.objects.create(
                **validated_data
            )
            return teacher

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['gender'] = '1' if instance.gender else '0'
        return representation
