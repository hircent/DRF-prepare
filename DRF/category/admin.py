from django.contrib import admin
from .models import Category, Theme, ThemeLesson

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'label', 'year', 'is_active')
    list_filter = ('name', 'year', 'is_active')
    search_fields = ('name',)
    ordering = ('name',)

class ThemeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order', 'category_label')
    list_filter = ('category__label',)
    search_fields = ('name',)
    ordering = ('name',)

    def category_label(self, obj):
        return obj.category.label

class ThemeLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'theme__name', 'name', 'order')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# Register your models here.

admin.site.register(Category, CategoryAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(ThemeLesson, ThemeLessonAdmin)
