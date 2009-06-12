from django.contrib import admin


class UpdateAdmin(admin.ModelAdmin):
    list_display = ('update_date', 'version', 'url', 'nb_devices',)
    list_filter = ('update_date',)
    search_fields = ('version', 'url',)
    
class PatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'created', 'active')
    list_filter = ('active', 'priority',)
    search_fields = ('name',)
