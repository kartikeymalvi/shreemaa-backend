from django.contrib import admin
from .models import CustomUser

# Ye accounts wale admin.py me hona chahiye
admin.site.register(CustomUser)