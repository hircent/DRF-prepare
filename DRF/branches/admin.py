from django.contrib import admin
from .models import Branch,BranchGrade

class BranchAdmin(admin.ModelAdmin):
    list_display = ("id","display_name","created_at","is_headquaters")

    search_fields =("display_name",)


class BranchGradeAdmin(admin.ModelAdmin):
    list_display = ("id","name","percentage","created_at")
# Register your models here.
admin.site.register(Branch,BranchAdmin)
admin.site.register(BranchGrade,BranchGradeAdmin)