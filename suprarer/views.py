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


class ProjectStatus:
    NEW = 1
    IN_PROGRESS = 2
    CLOSED = 3
    REJECTED = 4
    CONTEST = 5


class ProjectMemberStatus:
    MEMBER = 1
    REJECTED = 2
    ANSWERED = 3
    INVITED = 4
    OWNER = 5


class ProjectContestCreate(generics.CreateAPIView):
    serializer_class = ContestApprovementCreateSerializer
    permission_classes = [IsModerated]

    def post(self, request):
        data = request.data
        user = request.user
        project = data["project"]
        contest_requests = ContestApprovement.objects.filter(project__id=project)
        project_queryset = Project.objects.filter(id=project, status=ProjectStatus.IN_PROGRESS)
        project_director = ProjectMember.objects.filter(project__id=project, status=ProjectMemberStatus.OWNER,
                                                        member__user=user)
        if contest_requests:
            return Response(data="Вы уже подавали проект на конкурс. Играйте поправилам.",
                            status=status.HTTP_400_BAD_REQUEST)
        if not project_queryset:
            return Response(data="Проект не является активным :)", status=status.HTTP_403_FORBIDDEN)
        if not project_director:
            return Response(data="Вы не создатель или руководитель проекта", status=status.HTTP_403_FORBIDDEN)
        request_data_serializer = self.serializer_class(data=data)
        # проверяем валидность
        request_data_serializer.is_valid(raise_exception=True)
        # сохраняем данные в БД
        request_data_serializer.save()
        return Response(data=request_data_serializer.data, status=status.HTTP_201_CREATED)
