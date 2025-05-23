from rest_framework.response import Response
from rest_framework.views import APIView
from apps.competition.models import Competition
from apps.team.models import Team
from apps.student.models import Student
from apps.teacher.models import Teacher


class SearchView(APIView):
    def get(self, request, *args, **kwargs):
        key = request.query_params.get("key", "").strip()
        if not key:
            return Response({"code": 400, "message": "搜索关键字不能为空"})

        # 模糊搜索各个模型
        competitions = Competition.objects.filter(title__icontains=key, state=1, status='confirmed')
        teams = Team.objects.filter(name__icontains=key, state=1, status='confirmed')
        students = Student.objects.filter(username__icontains=key, state=1)
        teachers = Teacher.objects.filter(username__icontains=key, state=1)

        # 序列化结果（这里仅简单转换为字典）
        competition_results = [{"id": comp.id, "name": comp.title, "sn":  comp.sn} for comp in competitions]
        team_results = [{"id": team.id, "name": team.name, "sn": team.sn} for team in teams]
        student_results = [{"id": student.id, "name": student.username, "sn": student.sn} for student in students]
        teacher_results = [{"id": teacher.id, "name": teacher.username, "sn": teacher.sn} for teacher in teachers]

        return Response({
            "code": 200,
            "data": {
                "competitions": competition_results,
                "teams": team_results,
                "students": student_results,
                "teachers": teacher_results
            },
            "message": "搜索成功"
        })
