"""
URL configuration for graduation_django_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path

urlpatterns = [
    path('api/user/', include('apps.user.urls')),
    path('api/student/', include('apps.student.urls')),
    path('api/teacher/', include('apps.teacher.urls')),
    path('api/team/', include('apps.team.urls')),
    path('api/competition/', include('apps.competition.urls')),
    path('api/college/', include('apps.college.urls')),
    path('api/settings/', include('apps.settings.urls')),
    path('api/admin/', include('apps.admin.urls')),
    path('api/patent/', include('apps.patent.urls')),
    path('api/paper/', include('apps.paper.urls')),
]