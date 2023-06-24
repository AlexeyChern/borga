from django.contrib import admin
from .models import Loan, Borrower, Investor, Profile, Project, ProjectMember, Contest, ContestApprovement, MemberStatus



# Register your models here.

admin.site.register(Investor)
admin.site.register(Loan)
admin.site.register(Borrower)
admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(Contest)
admin.site.register(ContestApprovement)
admin.site.register(MemberStatus)