from django import forms
from django.contrib.auth.models import User
from .models import User,Booking,Product,Category,STATUS


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

class AddProductForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Enter product title", "class": "form-control"}))
    image = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control-file"}))
    description = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "Enter product description", "class": "form-control"}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={"class": "form-control"}))
    price = forms.DecimalField(widget=forms.NumberInput(attrs={"placeholder": "Enter product price", "class": "form-control"}))
    old_price = forms.DecimalField(widget=forms.NumberInput(attrs={"placeholder": "Enter old price", "class": "form-control"}))

    is_available = forms.BooleanField(widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    

    class Meta:
        model = Product
        fields = [
            'title','price','old_price','description','category','image','is_available'
        ]