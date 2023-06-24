from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render
from rest_framework import status
from rest_framework import generics, serializers
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Investor, Loan, Borrower, Project, ContestApprovement, ProjectMember
from .tasks import investor_task

import time


# Create your views here.

################# Task 12 - Проблема в том что транзакция еще не выполнена, поэтому shared_task не может получить query по запросу id
# Проблема в том что task пытается получить еще не существующий в базе объект, т.к. из за использования
# атомарности объект создается только в конце api_create_investor. Самым оптимальным на мой взгляд является
# перенос вызова task в transaction.on_commit, что запустит таск только после выполнения транзакции
# (тогда объект уже будет в базе). Также есть вариант добавить sleep перед запросом к базе из task,
# но это более "костыльно" и не надежно.
@transaction.atomic
@api_view(['POST'])
def api_create_investor(request):
    investor = Investor.objects.create()
    transaction.on_commit(lambda: investor_task.delay(investor.id))  ## Решение - on_commit
    time.sleep(0.5)
    return Response({"status": "OK"})


################## Task 13 - Некоторые бд могут дропнуть одновременный запрос к а и б (например скьюлайт - блокировка бд). Постгрес может с таким работать
# Проблема в том, что при одновременном обновлении может не сохранится одно из обновленных значений.
# К примеру если increase b произойдет чуть позже, то он сохранит в базу устаревшее значение a, даже если
# немного ранее оно было обновлено в своей функции. Как решение-блокировка базы до окончания транзакции при
# помощи select_for_update.
@api_view(['GET'])
@transaction.atomic
def api_increase_a(request, investor_id):
    investor = get_object_or_404(Investor.objects.select_for_update(), pk=investor_id)
    investor.a += 100

    time.sleep(5)  # эмуляция долгой работы метода - сама по себе проблемой не является
    investor.save()
    return Response({"status": "OK"})


@api_view(['GET'])
@transaction.atomic
def api_increase_b(request, investor_id):
    investor = get_object_or_404(Investor.objects.select_for_update(), pk=investor_id)
    print(Investor.objects.filter(b=999))
    if not Investor.objects.filter(b=999):
        print(1)
    investor.b += 100
    time.sleep(0.5)  # эмуляция долгой работы метода - сама по себе проблемой не является
    investor.save()
    return Response({"status": "OK"})


class ContestApprovementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestApprovement
        fields = "__all__"


### Если файла со статусами нет в проекте, я бы создал. Для текущего рефакторинга мне нужно:

class ProjectStatus:
    NEW = 1
    IN_PROGRESS = 2
    CLOSED = 3
    REJECTED = 4
    CONTEST = 5
class IsModerated:
    pass

class ProjectMemberStatus:
    MEMBER = 1
    REJECTED = 2
    RESPONDED = 3
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


# class ProjectContestCreate(generics.CreateAPIView):
#     queryset = ContestApprovement.objects.all()  ### Не используется, т.к. сам запрос переписан
#     serializer_class = ContestApprovementCreateSerializer
#     permission_classes = [IsModerated]
#
#     def post(self, request):
#         data = request.data
#         project = data['project']
#         contest_requests = ContestApprovement.objects.filter(project__id=project)
#         project_queryset = Project.objects.filter(id=project, status=2)  ### Лучше использовать именованные статусы
#         project_director = ProjectMember.objects.filter(project__id=project,
#                                                         status=5)  ### Лучше сразу проверять соответствует ли user,
#                                                                    ### тогда не придется по второму разу проверять
#                                                                    ###  project_director, использовать статусы
#         ### Вместо if-else можно писать просто if-return. После return дальше функция не пойдет.
#         if not len(contest_requests):  ### len не обязательно, пустой queryset == False
#             if len(project_queryset) & len(project_director) != 0:  ### Аналогично. Если len !=0 значит просто True
#                 if project_director.first().member.user == request.user:
#                     request_data = dict(data)  ### Это уже dict. Иначе мы не получим project.
#                     request_data['is_approved'] = "0"  ### В модели есть default значение, можно не указывать отдельно
#                     request_data = self.serializer_class(data=request_data)  ### Я бы использовал эту переменную только
#                     # для сериализатора, плюс лучше добавить в имя переменной что это сериализатор
#                     # проверяем валидность
#                     request_data.is_valid(raise_exception=True)
#                     # сохраняем данные в БД
#                     request_data.save()
#                     return Response(data=request_data.data,
#                                     status=status.HTTP_201_CREATED)
#                 else:
#                     return Response(data="Вы не создатель или руководитель проекта:)", status=status.HTTP_403_FORBIDDEN)
#             else:
#                 return Response(data="Вы не создатель или руководитель проекта| Проект не является активным :)",
#                                 status=status.HTTP_403_FORBIDDEN)
#         else:
#             return Response(data="Вы уже подавали проект на конкурс. Играйте поправилам.",
#                             status=status.HTTP_400_BAD_REQUEST)
