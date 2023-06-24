from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Project, ContestApprovement, ProjectMember


class ContestApprovementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestApprovement
        fields = "__all__"


### Класс-заглушка
class IsModerated(IsAuthenticated):
    pass


class ProjectContestCreate(generics.CreateAPIView):
    queryset = ContestApprovement.objects.all()
    serializer_class = ContestApprovementCreateSerializer
    permission_classes = [IsModerated]

    def post(self, request):
        data = request.data
        project = data['project']
        contest_requests = ContestApprovement.objects.filter(project__id=project)
        project_queryset = Project.objects.filter(id=project, status=2)
        project_director = ProjectMember.objects.filter(project__id=project,
                                                        status=5)
        if not len(contest_requests):
            if len(project_queryset) & len(project_director) != 0:
                if project_director.first().member.user == request.user:
                    request_data = dict(data)
                    request_data['is_approved'] = "0"
                    request_data = self.serializer_class(data=request_data)
                    # проверяем валидность
                    request_data.is_valid(raise_exception=True)
                    # сохраняем данные в БД
                    request_data.save()
                    return Response(data=request_data.data,
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response(data="Вы не создатель или руководитель проекта:)", status=status.HTTP_403_FORBIDDEN)
            else:
                return Response(data="Вы не создатель или руководитель проекта| Проект не является активным :)",
                                status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(data="Вы уже подавали проект на конкурс. Играйте поправилам.",
                            status=status.HTTP_400_BAD_REQUEST)
