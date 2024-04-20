from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Vendor, ProductReview, ProductImages, Booking
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
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
import json
from django.http import JsonResponse
from django.urls import reverse
from decimal import Decimal
import decimal
from django.views.decorators.csrf import csrf_exempt
from .utils import send_email_to_client
from django.core.files.storage import FileSystemStorage





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
    products = Product.objects.filter(product_status="published")

    context = {
        "products": products
    }

    return render(request, "product_list.html", context)


def product_detail_view(request, pid):
   
    product = get_object_or_404(Product, pid=pid)
    print(product.image.url)
    context = {
        "product": product
    }
    return render(request, "product_detail.html", context)

def settings(request):

    return render(request,"settings.html")
    

def my_bookings(request):
    if not request.user.is_authenticated:
        # Redirect to login page or show an error
        # Replace 'login_url' with your actual login page URL
        return redirect('login_url')

    # Retrieve all bookings for the current user
    bookings = Booking.objects.filter(
        user=request.user).order_by('-created_at')

    return render(request, 'my_bookings.html', {'bookings': bookings})


def check_availability(request, pid):
    product = get_object_or_404(Product, pid=pid)
    if request.method == 'POST':
        if product.is_available:
            start_date = request.POST.get('startDate')
            num_guests = request.POST.get('num_guests')
            request.session['start_date'] = start_date
            request.session['num_guests'] = num_guests
            request.session['package_id'] = pid
            details_url = reverse('booking_details', args=[product.id])
            return JsonResponse({'available': True, 'redirect_url': details_url})
        else:
            return JsonResponse({'available': False})
        

######################################### BOOKING DETAILS ####################################################


def booking_details(request, product_id):
    package_id = request.session.get('package_id')
    request.session['product_id'] = product_id
    product = get_object_or_404(Product, pid=package_id)
    start_date = request.session.get('start_date')
    num_guests = int(request.session.get('num_guests'))
    total_price = calculate_price(product, num_guests)
    transaction_id = uuid.uuid4().hex
    message = f"total_amount={ total_price},transaction_uuid={transaction_id},product_code=EPAYTEST"
    secret_code = "8gBm/:&EnhH.1/q"
    signature = generate_signature(message, secret_code)
    context = {
        'product': product,
        'start_date': start_date,
        'num_guests': num_guests,
        'total_price': total_price,
        'signature': signature,
        'message': message,
        'transaction_id': transaction_id,
        'package_id': package_id
    }
    return render(request, 'booking_details.html', context)


def calculate_price(product, num_guests):
    # Assuming 'base_price' is a field in your 'Product' model
    base_price = product.price
    price_per_guest = base_price
    total_price = price_per_guest * num_guests
    print(total_price)

    # Add additional logic for seasonal pricing or discounts
    if num_guests > 4:
        discount_factor = Decimal('0.90')  # Example: Bulk booking discount
        total_price *= discount_factor  # 10% discount for groups larger than four

    return total_price



def generate_signature(message, secret):
    message_bytes = message.encode('utf-8')
    secret_bytes = secret.encode('utf-8')
    hash_bytes = hmac.new(secret_bytes, message_bytes, hashlib.sha256).digest()
    hash_in_base64 = base64.b64encode(hash_bytes).decode('utf-8')
    return hash_in_base64


def clean_decimal(value):
    """Remove any unwanted characters from the decimal string."""
    return value.replace(',', '')



######################################### PAYMENT RESPONSE ####################################################


@csrf_exempt
def payment_response(request):
    encoded_data = request.GET.get('data')
    if not encoded_data:
        return JsonResponse({'status': 'error', 'message': 'No data provided'}, status=400)

    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    response_data = json.loads(decoded_data)
    transaction_status = response_data.get('status')

    if transaction_status == 'COMPLETE':
        # Extract necessary details from the response
        transaction_uuid = response_data.get('transaction_uuid')
        transaction_code = response_data.get('transaction_code')
        # Clean and prepare the total amount for decimal conversion
        total_amount_str = clean_decimal(response_data.get('total_amount'))
        total_amount = decimal.Decimal(total_amount_str)
        product_code = response_data.get('product_code')
        package_id = request.session.get('package_id')
        start_date = request.session.get('start_date')
        # Attempt to retrieve the product using the session stored package_id
        product = get_object_or_404(Product, pid=package_id)

        # Optionally find the user who made the booking, assuming authenticated session
        user = request.user if request.user.is_authenticated else None
        num_guests = request.session.get('num_guests')
        # Create or update the booking entry
        booking, created = Booking.objects.update_or_create(
            transaction_uuid=transaction_uuid,
            defaults={
                'user': user,
                'product': product,
                'total_price': total_amount,
                'transaction_code': transaction_code,
                'transaction_status': 'Completed',
                'check_in_date': start_date,
                'num_guests': num_guests,

            }
        )

        if user and user.email:
            subject = 'Booking Confirmation'
            message = f'Hi {user.username}, your booking for {product.title} on {start_date} has been confirmed.'
            recipient_list = [user.email]
            send_email_to_client(subject, message, recipient_list)

        return HttpResponseRedirect('/my-bookings/')

    else:
        return JsonResponse({'status': 'failed', 'message': 'Transaction incomplete'})

    return JsonResponse({'status': 'error', 'message': 'Unexpected error occurred'}, status=500)


######################################### SUBMIT BOOKING ####################################################

@login_required
def submit_booking(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        check_in_date = request.POST.get('check_in_date')
        num_guests = int(request.POST.get('num_guests')
                         )  # Ensure conversion to int

        product = Product.objects.get(pk=product_id)
        total_price = calculate_price(product, num_guests)

        booking = Booking.objects.create(
            user=request.user,
            product=product,
            check_in_date=check_in_date,
            num_guests=num_guests,
            total_price=total_price,
            special_requests=request.POST.get('special_requests', ''),
        )

        # Redirect to a booking confirmation page
        return redirect('booking_confirmation', booking_id=booking.id)

    else:
        # Handle GET request or show form again
        return render(request, 'booking_form.html')
    


######################################### CHANGE PASSWORD ####################################################

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
            # Handling specific error cases
            if 'old_password' in form.errors:
                messages.error(request, 'The old password is incorrect.')
            elif 'new_password2' in form.errors:
                messages.error(request, 'The new passwords do not match.')
            else:
                messages.error(request, 'Please verify the password below.')
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












def customize(request):
    return render(request,'customize.html')



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



################################################# VENDOR LOGIN ###################################################
@login_required
def vendor_dashboard(request):
    # Your vendor dashboard logic here
    return render(request, 'vendor_dashboard.html')

def vendor_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_vendor:  # Assuming is_vendor is a boolean field in your User model
            auth.login(request, user)
            messages.success(request, 'Successfully logged in as vendor')
            return redirect('vendor_dashboard')
        else:
            messages.error(request, 'Invalid vendor credentials')
            return redirect('vendor_login')
    else:
        return render(request, 'vendor_login.html')
    



################################################# VENDOR SIGNUP ###################################################


def vendor_register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        pan_card = request.FILES['pan_card']  # Access the uploaded PAN card image

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username Taken')
                return redirect('vendor_register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already Taken')
                return redirect('vendor_register')
            else:
                # Save the uploaded PAN card image to the media directory
                fs = FileSystemStorage()
                filename = fs.save(pan_card.name, pan_card)

                user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name)
                # Add additional fields specific to vendor registration to the user object
                user.save()
                messages.success(request, 'Registration successful. Please login.')
                return redirect('vendor_login')
        else:
            messages.error(request, 'Password does not match ')
            return redirect('vendor_register')

    else:
        return render(request, 'vendor_register.html')
