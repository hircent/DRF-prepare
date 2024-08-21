from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role

class UserAdmin(UserAdmin):
    model = User
    # Define which fields should be displayed on the admin site.
    list_display = ('first_name', 'last_name', 'email', 'is_superuser','is_superadmin','is_active')
    
    # Define which fields should be editable in the admin list view.
    list_editable = ('is_active',)
    
    # Define which fields to filter by in the admin list view.
    list_filter = ('is_superadmin', 'is_active', 'roles')
    
    # Define which fields should be displayed on the detail view page.
    fieldsets = (
        ('Login Credential', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'is_superadmin', 'roles')}),
        ('Important dates', {'fields': ('last_login', 'created_at','is_password_changed')}),
    )
    
    # Define which fields should be read-only.
    readonly_fields = ('created_at', 'last_login','is_password_changed')

    # Define which fields should be displayed for adding a new user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username','first_name', 'last_name', 'password1', 'password2','roles')}
        ),
    )
    
    # Define which fields should be used for searching users.
    search_fields = ('email', 'first_name', 'last_name')
    # ordering = ('email',)

    # Define which fields use a multi-select interface (for many-to-many fields).
    filter_horizontal = ('roles',)

class RoleAdmin(admin.ModelAdmin):
    list_display = ("id","name")
    ordering = ('id',)
# Register your models with the admin site.
admin.site.register(User, UserAdmin)
admin.site.register(Role,RoleAdmin)
