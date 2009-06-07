from django.db import models

class Update(models.Model):
    version = models.CharField(max_length=255)
    url = models.URLField()
    update_date = models.DateTimeField(auto_now_add=True)
    time_for_update = models.IntegerField()
    nb_devices = models.IntegerField()
    errors = models.TextField()
    
class Device(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    user_agent = models.CharField(max_length=255, blank=True, db_index=True)
    fall_back = models.CharField(max_length=128, blank=True, db_index=True)
    actual_device_root = models.BooleanField()
    capabilities = models.TextField()
