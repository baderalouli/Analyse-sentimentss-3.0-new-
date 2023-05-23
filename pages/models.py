from django.db import models

# Create your models here.


class Signup(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=50)
    confirm_password = models.CharField(max_length=50)


    def __str__(self):
        return self.username
