from django.contrib import admin
from .models import Students, StudentTransfer

class StudentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'fullname', 'first_name', 'branch', 'parent', 'status', 'enrolment_date')

    search_fields =('fullname',)
    
    list_filter = ('branch','status',)

class StudentTransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'from_branch', 'to_branch', 'transfer_date', 'status')
    
    search_fields =('student__fullname',)

    list_filter = ('from_branch','to_branch','status',)

    raw_id_fields = ('from_branch','to_branch','student',)

admin.site.register(Students, StudentsAdmin)
admin.site.register(StudentTransfer, StudentTransferAdmin)
