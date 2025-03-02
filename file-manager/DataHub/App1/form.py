from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]
        labels = {
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'password': 'Password',
        }

        help_texts = {  
            'username': '',
        }

        widgets = {

            'username': forms.TextInput(attrs={'placeholder': 'Username','class': 'form-control mb-4'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name','class': 'form-control mb-4'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name','class': 'form-control mb-4'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Valid Email','class': 'form-control mb-4'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Strong Password','class': 'form-control mb-4'}),
        }

