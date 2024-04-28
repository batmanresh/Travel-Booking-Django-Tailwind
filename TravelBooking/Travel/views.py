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
from .forms import EditProfileForm 
from .decorators import allowed_users,vendor_only
from django.contrib.auth.decorators import login_required
from .forms import AddProductForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login




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
    product_images = ProductImages.objects.filter(product=product)
    context = {
        "product": product,
        "product_images": product_images
    }
    return render(request, "product_detail.html", context)

def settings(request):

    return render(request,"settings.html")

def search_results(request):
    search_query = request.GET.get('q', '')

    search_results = Product.objects.filter(title__icontains=search_query) | Product.objects.filter(description__icontains=search_query)

    context = {
        'search_query': search_query,
        'search_results': search_results,
    }

    return render(request, 'search_results.html', context)




def compare_products(request):
    products = Product.objects.all()
    selected_products = None
    comparison_result=None

    if request.method == 'POST':
        selected_product1_id = request.POST.get('selected_product1')
        selected_product2_id = request.POST.get('selected_product2')
        
        selected_product1 = Product.objects.get(id=selected_product1_id)
        selected_product2 = Product.objects.get(id=selected_product2_id)
        
        
        comparison_result = {}

        
        if selected_product1.price < selected_product2.price:
            comparison_result['price'] = f"{selected_product1.title} is cheaper than {selected_product2.title}"
        elif selected_product1.price > selected_product2.price:
            comparison_result['price'] = f"{selected_product2.title} is cheaper than {selected_product1.title}"
        else:
            comparison_result['price'] = "Prices are the same"

        selected_products = [selected_product1, selected_product2]

    return render(request, 'compare.html', {'products': products, 'selected_products': selected_products, 'comparison_result': comparison_result})




@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('settings')  
        else:
            messages.error(request, 'Error updating profile. Please correct the errors below.')
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form})




@login_required(login_url="login")
def my_bookings(request):
    if not request.user.is_authenticated:
        
        return redirect('login_url')

    
    bookings = Booking.objects.filter(
        user=request.user).order_by('-created_at')

    return render(request, 'my_bookings.html', {'bookings': bookings})

@login_required(login_url="login")
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


@login_required(login_url="login")
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
    
    base_price = product.price
    price_per_guest = base_price
    total_price = price_per_guest * num_guests
    print(total_price)

    
    if num_guests > 4:
        discount_factor = Decimal('0.90')  
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

@login_required(login_url="login")
def submit_booking(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        check_in_date = request.POST.get('check_in_date')
        num_guests = int(request.POST.get('num_guests')
                         )  

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

        
        return redirect('booking_confirmation', booking_id=booking.id)

    else:
        
        return render(request, 'booking_form.html')
    


######################################### CHANGE PASSWORD ####################################################

@login_required(login_url="login")
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Your password was successfully changed!')
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


@login_required(login_url='login')
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('index')  
    return render(request, 'delete_account.html')


def checkout(request):
    return render(request, 'checkout.html')

def customize(request):
    return render(request,'customize.html')












######################################################################## ADD PRODUCT ###############################################################################

@vendor_only
def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            form.save_m2m()
            messages.success(request, "Product added successfully.")
            return redirect("vendor_dashboard")  
    else:
        form = AddProductForm()

    context = {
        "form": form,
    }

    return render(request, "vendor_add_product.html", context)



######################################################################## SIGNUP ###############################################################################

from django.contrib import messages

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            username = request.POST['username']
            email = request.POST['email']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
             

            if password1 == password2:
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username Taken')
                    return redirect('register')
                elif User.objects.filter(email=email).exists():
                    messages.error(request, 'Email already Taken')
                    return redirect('register')
                else:
                    user = User.objects.create_user(username=username, password=password1, email=email, last_name=last_name,
                                                    first_name=first_name)
                      
                    user.save()
                    messages.success(request, 'Account created successfully. You can now login.')
                    return redirect('login')
            else:
                messages.error(request, 'Password does not match ')
                return redirect('register')

        else:
            return render(request, 'register.html')


        


######################## LOGIN ###############################



def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.groups.filter(name__in=['vendor', 'admin']).exists():
                    messages.error(request, 'Vendors and admins are not allowed to log in.')
                    return redirect('login')
                else:
                    auth_login(request, user)
                    messages.success(request, 'Successfully logged in.')
                    return redirect('index')
            else:
                messages.error(request, 'Invalid credentials.')
                return redirect('login')
        else:
            return render(request, 'login.html')



def logout(request):
    auth.logout(request)
    messages.success(request, 'Logged Out Successfully')
    return redirect('index')



################################################# VENDOR LOGIN ###################################################
@allowed_users(allowed_roles=['vendor'])
@vendor_only
@login_required(login_url= "vendor_login")
def vendor_dashboard(request):
    # Your vendor dashboard logic here
    return render(request, 'vendor_dashboard.html')


def vendor_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.groups.filter(name='vendor').exists():
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
        pan_card = request.FILES['pan_card']  

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username Taken')
                return redirect('vendor_register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already Taken')
                return redirect('vendor_register')
            else:
                
                fs = FileSystemStorage()
                filename = fs.save(pan_card.name, pan_card)

                user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name)
                
                user.save()
                messages.success(request, 'Registration successful. Please login.')
                return redirect('vendor_login')
        else:
            messages.error(request, 'Password does not match ')
            return redirect('vendor_register')

    else:
        return render(request, 'vendor_register.html')




