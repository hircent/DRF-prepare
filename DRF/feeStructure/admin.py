from django.contrib import admin
from .models import Tier, Grade, State
# Register your models here.

class GradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'grade_level', 'get_state', 'get_tier', 'category', 'price')
    list_filter = ('category', 'tier__state', 'tier')
    search_fields = ('grade_level',)
    ordering = ('grade_level',)

    def get_state(self, obj):
        return obj.tier.state.state_name
    get_state.short_description = 'State'
    
    def get_tier(self, obj):
        return obj.tier.name
    get_tier.short_description = 'Tier'

class TierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'created_at', 'updated_at')
    list_filter = ('name','year',)
    search_fields = ('name',)

class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'state_name', 'state_code')
    list_filter = ('state_name',)
    search_fields = ('state_name',)

admin.site.register(State, StateAdmin)
admin.site.register(Tier, TierAdmin)
admin.site.register(Grade, GradeAdmin)