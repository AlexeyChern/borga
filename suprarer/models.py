from django.db import models


class Investor(models.Model):
    name = models.CharField(max_length=300)
    processed = models.BooleanField(default=False)
    a = models.IntegerField(default=0)
    b = models.IntegerField(default=1)


class Borrower(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=127, default='')


class Loan(models.Model):
    STATUS_CHOICES = [
        (0, 'new'),
        (1, 'active'),
        (2, 'closed'),
    ]

    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    borrower = models.ForeignKey(Borrower, models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=12, decimal_places=2)


class Project(models.Model):
    status = models.IntegerField(default=1)
    name = models.CharField(max_length=100, default="Unnamed")


class Profile(models.Model):
    name = models.CharField(max_length=100, default="Boba")


class MemberStatus(models.Model):
    status = models.IntegerField(default=1)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)


class ProjectMember(models.Model):
    project = models.ForeignKey(Project, verbose_name="Проект", on_delete=models.CASCADE)
    member = models.ForeignKey(Profile, verbose_name="Участник", on_delete=models.CASCADE)
    status = models.ForeignKey(MemberStatus, verbose_name="Статус юзера", on_delete=models.CASCADE)
    comment = models.TextField(verbose_name="Комментарий пользователя", null=True, blank=True)

class Contest(models.Model):
    name = models.CharField(max_length=100, default="No name")

class ContestApprovement(models.Model):
    STATUS_CHOICES = (
        ("0", "Waiting"),
        ("1", "Accepted"),
        ("2", "Declined")
    )
    project = models.ForeignKey(Project, verbose_name="Проект", on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, verbose_name="Конкурс", on_delete=models.CASCADE)
    is_approved = models.CharField(verbose_name="Проект принят", max_length=1, choices=STATUS_CHOICES, default="0")

    class Meta:
        unique_together = ("contest", "project")
