from django.contrib import admin
from .models import Branch

class BranchAdmin(admin.ModelAdmin):
    list_display = ("id","name","created_at")
# Register your models here.
admin.site.register(Branch,BranchAdmin)