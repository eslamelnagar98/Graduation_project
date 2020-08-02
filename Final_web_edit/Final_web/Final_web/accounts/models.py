from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from Final_web.settings import AUTH_USER_MODEL
from django.utils.text import slugify
import datetime

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        """
        Create and save a User with the given username and password.
        """
        if not username:
            raise ValueError(_('username must be set'))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    phone_regex = RegexValidator(regex=r'^\+?01[0125]\d{8}$',
                                 message="Phone number must be entered in the format: '01214448796'. ")

    GENDER_CHOICES = [
        ('F', 'Female'),
        ('M', 'Male'),
    ]

    age = models.IntegerField(default=10)
    phone_number = models.CharField(max_length=12,validators=[phone_regex])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    is_doctor = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_patient = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )



    def __str__(self):
        return self.username


class Doctor(User):
    def save(self, *args, **kwargs):
        self.is_doctor = True
        super().save()


class Patient(User):
    phone_regex = RegexValidator(regex=r'^\+?01[0125]\d{8}$',
                                 message="Phone number must be entered in the format: '01214448796'. ")

   # doctor_number = models.CharField(validators=[phone_regex], max_length=17)
    emergency_number = models.CharField(validators=[phone_regex], max_length=17)
    slug = models.SlugField(("slug"), blank=True, null=True)
    doctors=models.ManyToManyField(Doctor)

    objects = CustomUserManager()


    def save(self, *args, **kwargs):
        self.is_patient = True
        if not self.slug:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class DoctorPatientRequest(models.Model):
    NEW = 'NEW'
    STATUS_CHOICES = [
        (NEW, 'New'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES ,default=NEW)


class pulses(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    heart_beat=models.FloatField(null=True)
    time = models.DateTimeField(default=datetime.datetime.now)



class PatientRecords(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    time=models.DateTimeField()
    potential_energy=models.FloatField()
    pulse=models.ForeignKey(pulses,on_delete=models.CASCADE)

class DoctorComments(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    comment = models.TextField(max_length=300)


class subscribers(models.Model):
    email=models.EmailField()




