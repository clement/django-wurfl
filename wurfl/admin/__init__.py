from django.contrib import admin
from wurfl.models import Update, Patch
from wurfl.admin.models import UpdateAdmin, PatchAdmin

# Register WURFL Updates
admin.site.register(Update, UpdateAdmin)
admin.site.register(Patch, PatchAdmin)
