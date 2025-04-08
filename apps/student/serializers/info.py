from rest_framework import serializers
from apps.student.models import Student
import logging

logger = logging.getLogger('student')

class StudentSerializer(serializers.ModelSerializer):

    cn = serializers.CharField(write_only=True, required=False)
    cn_1 = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'username', 'email',
            'gender', 'phone', 'cn',
            'cn_1',
            'prize_num', 'race_num', 'college_id'
        ]
        extra_kwargs = {
            'username': {'read_only': True},
            'id': {'read_only': True},
            'college_id': {'read_only': True},
        }

    def get_cn_1(self, obj):
        """解密cn字段的方法"""
        try:
            # 调用模型的解密方法
            return obj.get_cn()
        except Exception as e:
            logger.error(f"解密身份证信息失败: {str(e)}")
            return None

    def update(self, instance, validated_data):
        """重写update方法，对身份证号码进行加密处理"""
        new_cn = validated_data.get('cn')
        if new_cn:
            try:
                # 调用模型的加密方法
                instance.set_cn(new_cn)
            except Exception as e:
                logger.error(f"加密身份证信息失败: {str(e)}")
                raise serializers.ValidationError({'cn': '身份证号码加密失败'})

        # 更新其他字段
        for attr, value in validated_data.items():
            if attr != 'cn':  # 已经处理了cn字段
                setattr(instance, attr, value)

        instance.save()
        return instance