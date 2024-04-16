from django.shortcuts import render,redirect,get_object_or_404
from .models import Product, Category, Vendor, ProductReview, ProductImages, Booking
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import *
from django import forms
from django.db.models import Count
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import uuid
from shortuuid.django_fields import ShortUUIDField
import hmac
import hashlib
import base64



# Create your views here.
def base(request):
    return render(request, "base.html")

def index(request):
    products=Product.objects.filter(product_status="published",featured=True)

    context={
        "products":products
    }

    return render(request, "index.html", context)

def product_list_view(request):
    products=Product.objects.filter(product_status="published")

    context={
        "products":products
    }

    return render(request, "product_list.html", context)


def product_detail_view(request, pid):
    product=Product.objects.get(pid=pid)
    
    p_image=product.p_images.all()

    context={
        "p":product,
        "p_image":p_image,
    }

    return render(request,"product_detail.html",context)

def settings(request):

    return render(request,"settings.html")
    

def check_availability(request):
    if request.method == 'POST':
        # Retrieve form data
        start_date = request.POST.get('startDate')
        num_guests = request.POST.get('num_guests')
        package_id = request.POST.get('pid')
        
      
        
        # Store the user-entered information into the session
        request.session['start_date'] = start_date
        request.session['num_guests'] = num_guests
        request.session['package_id'] = package_id 

        
        # Redirect to the booking_detail view
        return redirect('booking_detail', package_id=package_id)
    else:
        # Handle GET request if necessary
        pass
def generate_signature(message, secret):
    # Convert the message and secret to bytes
    message_bytes = message.encode('utf-8')
    secret_bytes = secret.encode('utf-8')

    # Generate the hash using HMAC SHA-256
    hash_bytes = hmac.new(secret_bytes, message_bytes, hashlib.sha256).digest()

    # Convert the hash to Base64 string
    hash_in_base64 = base64.b64encode(hash_bytes).decode('utf-8')

    return hash_in_base64

def booking_detail(request, package_id):
    # Retrieve package details
    package = Product.objects.get(pid=package_id)
    print(package)
    # Retrieve user-entered information from the session
    start_date = request.session.get('start_date')
    num_guests = request.session.get('num_guests')
    # Generate random transaction ID
    transaction_id = uuid.uuid4().hex
    message = f"total_amount={package.price},transaction_uuid={transaction_id},product_code=EPAYTEST"
    secret_code="8gBm/:&EnhH.1/q"
    signature = generate_signature(message, secret_code)

    # Check if start_date and num_guests are available in the session
    # if start_date is None or num_guests is None :
    #     # If not, redirect to the previous page or show an error message
    #     messages.error(request, 'Please enter your check-in date and number of guests first.')
    #     return redirect('product_detail', package_id=package_id)
    
    # Render the booking detail template with package details and user information
    context = {
        'package': package,
        'start_date': start_date,
        'num_guests': num_guests,
        'transaction_id': transaction_id,
        'signature':signature
      
    }
    return render(request, 'booking_detail.html', context)
# def booking_details(request):
#     # Your view logic here
#     return render(request, 'booking_details.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # To keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('settings')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('index')  # Redirect to the homepage or login page after account deletion
    return render(request, 'delete_account.html')


def checkout(request):
    return render(request, 'checkout.html')



######################## SIGNUP ###############################

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.success(request, 'Username Taken')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.success(request, 'Email already Taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, password=password1, email=email, last_name=last_name,
                                                first_name=first_name)
                user.save()
                print('User Created')
                return redirect('login')
        else:
            messages.success(request, 'Password does not match ')
            return redirect('register')

    else:
        return render(request, 'register.html')
    


######################## LOGIN ###############################

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Sucessfully Logged in')
            return  redirect('index')
        else:
            messages.error(request, 'Invalid credential')
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    messages.success(request, 'Logged Out Successfully')
    return redirect('index')

