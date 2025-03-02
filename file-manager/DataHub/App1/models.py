from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class FileTypes(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories", null=False, blank=False)
    created_at = models.DateTimeField(auto_now=True)

class Folders(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now=True)

class Uploads(models.Model):
    name  = models.CharField(max_length=300, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=2048)
    category = models.ForeignKey(FileTypes, on_delete=models.CASCADE, related_name='uploads', null=False, blank=False)
    size = models.BigIntegerField()
    upload_time = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-upload_time"]