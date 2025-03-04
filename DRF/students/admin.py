from django.contrib import admin
from .models import Students

class StudentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'fullname', 'first_name', 'branch', 'parent', 'status', 'enrolment_date')

    search_fields =('fullname',)
    
    list_filter = ('branch','status',)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'parent':
    #         # Filter only users who have the 'parent' role
    #         kwargs['queryset'] = UserBranchRole.objects.filter(role__name='parent').values_list('user__username', flat=True)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Students, StudentsAdmin)
