from django.contrib import admin
from .models import Branch,BranchGrade,UserBranchRole,BranchAddress

class BranchAdmin(admin.ModelAdmin):
    list_display = ("id","display_name","created_at","is_headquaters")

    search_fields =("display_name",)

class BranchAddressAdmin(admin.ModelAdmin):
    list_display = ("id","branch","address_line_1","city","state")

    search_fields =("branch__name",)


class BranchGradeAdmin(admin.ModelAdmin):
    list_display = ("id","name","percentage","created_at")

class UserBranchRoleAdmin(admin.ModelAdmin):
    # Specify the fields to display in the list view
    list_display = ('user', 'branch', 'role', 'created_at', 'updated_at')
    
    # Add search functionality to search by user, branch, and role
    search_fields = ('user__username', 'branch__name', 'role__name')
    
    # Add filters for branch and role to filter the displayed entries
    list_filter = ('branch', 'role', 'created_at')
    
    # Specify the fields to display in the detail view when editing a specific UserBranchRole
    fields = ('user', 'branch', 'role')

    # Add readonly fields to prevent editing of created_at and updated_at timestamps
    readonly_fields = ('created_at', 'updated_at')
# Register your models here.


admin.site.register(Branch,BranchAdmin)
admin.site.register(BranchAddress,BranchAddressAdmin)
admin.site.register(BranchGrade,BranchGradeAdmin)
admin.site.register(UserBranchRole,UserBranchRoleAdmin)