from django.contrib import admin
from .models import StudentCertificate
# Register your models here.
class StudentCertificateAdmin(admin.ModelAdmin):
    list_display = ('student','grade','branch','start_date','end_date','status','is_printed')
    list_filter = ('student','grade','branch')

    raw_id_fields = ('student','grade','branch')

admin.site.register(StudentCertificate,StudentCertificateAdmin)