from django.db import models
from main_app.func import hash_upload


class DocumentTex(models.Model):
    filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=hash_upload)
