from django.contrib import admin
from .models import Tier, Grade, TierGradeFees
# Register your models here.

class GradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'grade_level', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('grade',)
    ordering = ('grade_level',)

class TierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    list_filter = ('name',)
    search_fields = ('name',)

class TierGradeFeesAdmin(admin.ModelAdmin):
    list_display = ('id', 'tier', 'grade', 'fee')
    list_filter = ('tier', 'grade')
    search_fields = ('tier', 'grade')

admin.site.register(TierGradeFees, TierGradeFeesAdmin)
admin.site.register(Tier, TierAdmin)
admin.site.register(Grade, GradeAdmin)