from django import forms
from django.contrib.auth.models import User
from .models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User  # Assuming you have a Profile model associated with the User model
        fields = ['first_name', 'last_name']  # Specify the fields you want to edit
