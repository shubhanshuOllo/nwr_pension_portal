from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.fullname
