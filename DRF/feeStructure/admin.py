from django.contrib import admin
from .models import Tier, Grade, State
# Register your models here.

class GradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'grade_level', 'get_tier', 'get_country','category', 'price')
    list_filter = ('category', 'tier','tier__country',)
    search_fields = ('grade_level',)
    ordering = ('grade_level',)
    
    def get_tier(self, obj):
        return obj.tier.name
    get_tier.short_description = 'Tier'

    def get_country(self, obj):
        return obj.tier.country.name
    get_country.short_description = 'Country'

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