# Generated by Django 4.1.7 on 2023-06-21 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "suprarer",
            "0005_contest_memberstatus_profile_project_projectmember_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="name",
            field=models.CharField(default="Unnamed", max_length=100),
        ),
    ]
