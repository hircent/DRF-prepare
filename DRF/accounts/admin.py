from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SuperAdmin

class AccountAdmin(UserAdmin):
    model = SuperAdmin
    # Define which fields should be displayed on the admin site.
    list_display = ('email', 'first_name', 'last_name', 'is_admin', 'is_active', 'is_superadmin')
    
    # Define which fields should be editable in the admin list view.
    list_editable = ('is_active', 'is_superadmin')
    
    # Define which fields to filter by in the admin list view.
    list_filter = ('is_admin', 'is_active', 'is_superadmin')
    
    # Define which fields should be displayed on the detail view page.
    fieldsets = (
        ('Login Credential', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superadmin')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Define which fields should be read-only.
    readonly_fields = ('date_joined', 'last_login')

    # Define which fields should be displayed for adding a new user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_superadmin')}
        ),
    )
    
    # Define which fields should be used for searching users.
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    filter_horizontal = ()

# Register your models with the admin site.
admin.site.register(SuperAdmin, AccountAdmin)
