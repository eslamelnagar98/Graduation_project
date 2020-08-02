from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
    EmailField,

)
from django.core.validators import RegexValidator

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework import exceptions
from rest_framework.validators import UniqueValidator

from .models import Patient, DoctorPatientRequest, User, Doctor, PatientRecords, DoctorComments,pulses


class User_register_serlizer(serializers.ModelSerializer):
    email = serializers.EmailField(label='Email adress', validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'age', 'email']

    def validate_password(self, password):
        return password


class patient_register_serlizer(User_register_serlizer):
    phone_regex = RegexValidator(regex=r'^\+?01[0125]\d{8}$',
                                 message="Phone number must be entered in the format: '01214448796' ")
    phone_number = serializers.CharField(validators=[phone_regex], max_length=17)
    # doctor_number = serializers.CharField(validators=[phone_regex], max_length=17)
    emergency_number = serializers.CharField(validators=[phone_regex], max_length=17)

    #  email = EmailField(label='Email adress')
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    gender = serializers.ChoiceField(
        choices=[('M', 'male'), ('F', 'female')],
        style={'base_template': 'radio.html'}
    )

    class Meta:
        model = Patient
        fields = User_register_serlizer.Meta.fields + ['phone_number', 'emergency_number', 'gender',
                                                       'username', 'password']

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")

        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = Patient.objects.create_user(**validated_data)
        return user


class DoctorSerializer(User_register_serlizer):
    class Meta:
        model = Doctor
        fields = User_register_serlizer.Meta.fields + ['phone_number', 'gender', 'username', ]

    def validate_email(self, value):
        email = value
        user_qs = Doctor.objects.filter(email=email)
        if user_qs.exists():
            raise ValidationError("Email alredy registred")
        return value


#
class Update_Patient(User_register_serlizer):
    # username= serializers.CharField( read_only=True,)
    gender = serializers.ChoiceField(
        choices=[('M', 'male'), ('F', 'female')],
        style={'base_template': 'radio.html'}
    )
    phone_regex = RegexValidator(regex=r'^\+?01[0125]\d{8}$',
                                 message="Phone number must be entered in the format: '01214448796' ")
    emergency_number = serializers.CharField(validators=[phone_regex], max_length=17)
    phone_number = serializers.CharField(validators=[phone_regex], max_length=17, allow_null=True)

    class Meta:
        model = Patient
        fields = User_register_serlizer.Meta.fields + ['phone_number', 'emergency_number', 'gender',
                                                       'username']

    def validate_email(self, value):
        # self.instance is the current instance (Administrator)
        # this method is called on every request, so you should do
        # if self.instance
        # to check if the method is update/post, so you can have an instance
        # and then you do the check for the username uniqueness
        if self.instance and User.objects.exclude(pk=self.instance.pk).filter(email=value):
            raise serializers.ValidationError('User with this email already exists.')

        return value


class RequestSerializer(ModelSerializer):
    class Meta:
        model = DoctorPatientRequest
        fields = [
            'id',
            'patient',
            'doctor',
            'status',
        ]


class RequestSerializer_2(ModelSerializer):
    class Meta:
        model = DoctorPatientRequest
        fields = [
            'status',

        ]


class RecordsListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        if len(validated_data) > 215 and len(validated_data)<215:
            raise ValidationError('Must be 215 record')
        #print(validated_data)
        pulse = pulses.objects.create(patient_id=validated_data[0]['patient'].id)
        records = [PatientRecords(**item) for item in validated_data]
        for r in records:
            r.pulse_id = pulse.id
        with transaction.atomic():
            try:
                print(validated_data[0])
                records = PatientRecords.objects.bulk_create(records)
            except IntegrityError as ex:
                raise ValidationError(ex)
        return records




class RecordsSerializer(ModelSerializer):
    class Meta:
        model = PatientRecords
        fields = [
            'id',
            'patient',
            'time',
            'potential_energy',
            'pulse_id',
        ]
        list_serializer_class = RecordsListSerializer






class CommentsSerializer(ModelSerializer):
    class Meta:
        model = DoctorComments
        fields = [
            'id',
            'patient',
            'doctor',
            'comment',
        ]

class heartbeatSerializer(ModelSerializer):
    class Meta:
        model = pulses
        fields = [
            'id',
            'heart_beat',
            'patient',
            'time',
        ]






# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(
#         write_only=True,
#         required=True,
#         help_text='Leave empty if no change needed',
#         style={'input_type': 'password', 'placeholder': 'Password'}
#     )
#
#     def validate(self, data):
#         username = data.get("username", "")
#         password = data.get("password", "")
#
#         if username and password:
#             user = authenticate(username=username, password=password)
#             if user:
#                 if user.is_patient:
#                     if user.is_active:
#                         data["user"] = user
#                     else:
#                         msg = "User is deactivated."
#                         raise exceptions.ValidationError(msg)
#                 else:
#                     msg = "You are not Authorized To login."
#                     raise exceptions.ValidationError(msg)
#             else:
#                 msg = "Unable to login with given credentials."
#                 raise exceptions.ValidationError(msg)
#         else:
#             msg = "Must provide username and password both."
#             raise exceptions.ValidationError(msg)
#         return data
#
#        # status = serializers.HiddenField(default=timezone.now)
