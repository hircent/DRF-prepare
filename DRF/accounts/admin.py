from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role ,UserProfile
from django.contrib.auth.models import Group

admin.site.unregister(Group)

class UserAdmin(UserAdmin):
    model = User
    # Define which fields should be displayed on the admin site.
    list_display = ("id",'email', 'username', 'email','is_superadmin','is_active')
    
    # Define which fields should be editable in the admin list view.
    list_editable = ('is_active',)
    
    # Define which fields to filter by in the admin list view.
    list_filter = ("id",'is_superadmin', 'is_active')
    
    # Define which fields should be displayed on the detail view page.
    fieldsets = (
        ('Login Credential', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('id','first_name', 'last_name', 'username')}),
        ('Permissions', {'fields': ('is_active','is_superadmin')}),
        ('Important dates', {'fields': ('last_login', 'created_at','updated_at','is_password_changed')}),
    )
    
    # Define which fields should be read-only.
    readonly_fields = ('id','created_at', 'last_login','is_password_changed','updated_at')

    # Define which fields should be displayed for adding a new user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username','first_name', 'last_name', 'password1', 'password2')}
        ),
    )
    
    # Define which fields should be used for searching users.
    search_fields = ('email', 'first_name', 'last_name')
    # ordering = ('email',)

    # Define which fields use a multi-select interface (for many-to-many fields).
    filter_horizontal = ()

class RoleAdmin(admin.ModelAdmin):
    list_display = ("id","name")
    ordering = ('id',)
    
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id","user","gender","personal_email")
# Register your models with the admin site.
admin.site.register(User, UserAdmin)
admin.site.register(Role,RoleAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
