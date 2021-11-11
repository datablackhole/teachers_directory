from django.db import models

from django.contrib.auth.models import User
from datetime import datetime






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
