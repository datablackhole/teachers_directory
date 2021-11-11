from django.db import models

from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile',primary_key=True)
    email_verification_token = models.CharField( max_length =240)
    #   def __str__(self):
    # return self.title






# Create your models here.
class Teachers(models.Model):
    first_name = models.CharField( max_length =240)
    last_name = models.CharField( max_length =240)
    profile_picture = models.ImageField()
    email_address = models.CharField( max_length =240)
    phone_number = models.CharField( max_length =240)
    room_number = models.CharField( max_length =240)
    subjects_taught = models.CharField( max_length =240)
    



class Subjects(models.Model):
    subject_name = models.CharField( max_length =240)
