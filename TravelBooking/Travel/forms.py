from django import forms
from django.contrib.auth.models import User
from .models import User,Booking

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User  # Assuming you have a Profile model associated with the User model
        fields = ['first_name', 'last_name']  # Specify the fields you want to edit



class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['product', 'check_in_date', 'num_guests', 'special_requests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'special_requests': forms.Textarea(attrs={'rows': 4}),
        }

        
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']