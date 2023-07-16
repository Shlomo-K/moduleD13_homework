from django.db import models
from django.contrib.auth.models import AbstractUser

class MyUser(AbstractUser):
    enabled = models.BooleanField(default = False)