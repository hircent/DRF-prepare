from django.contrib import admin
from .models import Category, Theme, Grade

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'is_active')
    list_filter = ('name', 'year', 'is_active')
    search_fields = ('name',)
    ordering = ('name',)

class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_label')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('name',)

    def category_label(self, obj):
        return obj.category.label

class GradeAdmin(admin.ModelAdmin):
    list_display = ('grade_level', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('grade',)
    ordering = ('grade_level',)


# Register your models here.

admin.site.register(Category, CategoryAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Grade, GradeAdmin)
