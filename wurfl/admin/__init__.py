from django.contrib import admin
from wurfl.models import Update
from wurfl.admin.models import UpdateAdmin

# Register WURFL Updates
admin.site.register(Update, UpdateAdmin)
