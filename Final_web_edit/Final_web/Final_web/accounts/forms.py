from django import forms
from django.urls import reverse_lazy
from parsley.decorators import parsleyfy
from django.core.exceptions import ValidationError

from .models import Doctor
from django.contrib.auth import get_user_model
from datetime import date
from django.utils.safestring import mark_safe
User = get_user_model()


@parsleyfy
class SignUpForm(forms.ModelForm):
    password2 = forms.CharField(label='Comfirm Password', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
    GENDER_CHOICES = (('M', 'male'), ('F', 'female'))
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect(attrs={'class': 'radio-inline'}),)
    date_of_birth=forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'),label='Date of birth (DD/MM/YYYY)')

    class Meta:
        model = Doctor
        fields = (
            'first_name', 'last_name','date_of_birth',
            'email', 'gender','phone_number', 'username',
            'password'
        )


    extra_kwargs = {"password":
                        {"write_only": True},
                        "id":
                        {"read_only": True}
                        },



    def clean_email(self):

        email = self.cleaned_data.get('email')
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('This email address is already in use.')



    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password != password2:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput(attrs={'autocomplete': 'off'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'autocomplete': 'off'})
        self.fields['email'].required = True


class LoginForm(forms.Form):

    username = forms.CharField()
    password = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput(attrs={'autocomplete': 'off'})

class UserUpdateForm(forms.ModelForm):
    class Meta:
        first_name= forms.CharField()
        last_name=forms.CharField()
        email=forms.CharField()
        age = forms.CharField()
        phone = forms.CharField()
        model = Doctor
        fields = ('first_name', 'last_name', 'email', 'age', 'phone_number')

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.instance and User.objects.exclude(pk=self.instance.pk).filter(email=email):
            raise forms.ValidationError('User with this email already exists.')
        return email





