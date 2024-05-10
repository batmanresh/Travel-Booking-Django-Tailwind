from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Vendor, ProductReview, ProductImages, Booking, ContactMessage
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
from .forms import EditProfileForm,AddProductForm,ContactForm
from .decorators import allowed_users,vendor_only
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import Group
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordResetForm
from django.views.generic.edit import FormView
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q




# Create your views here.

def base(request):
    return render(request, "base.html")

def index(request):
    products = Product.objects.filter(product_status="published", featured=True, status=True)
    categories = Category.objects.all()  # Fetch all categories
    
    context = {
        "products": products,
        "categories": categories,  # Include categories in the context
    }

    return render(request, "index.html", context)


def product_list_view(request, category_slug=None):
    category = None
    products = Product.objects.filter(product_status="published",status=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    categories = Category.objects.all()

    context = {
        "category": category,
        "products": products,
        "categories": categories
    }

    return render(request, "product_list.html", context)

def filtered_product_list_view(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(product_status="published", category=category,status=True)
    categories = Category.objects.all()

    context = {
        "category": category,
        "products": products,
        "categories": categories
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

    search_results = Product.objects.filter(
        Q(title__icontains=search_query) | Q(category__title__icontains=search_query),
        product_status="published",
        status=True
    )


    context = {
        'search_query': search_query,
        'search_results': search_results,
    }

    return render(request, 'search_results.html', context)




def compare_products(request):
    products = Product.objects.filter(product_status="published",status=True)
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



def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., send an email)
            # You can access the form fields using form.cleaned_data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Handle the form data as needed (e.g., send an email)

            # Redirect to a success page or display a success message
            return redirect('contact_success')  # Replace 'success_page' with the URL name of your success page
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def contact_success(request):
    return render(request, 'contact_success.html')



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
        num_guests = int(request.POST.get('num_guests', 0))
        if product.is_available and product.sku >= num_guests:
            start_date = request.POST.get('startDate')
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
from django.http import HttpResponseBadRequest
@login_required(login_url="login")
def submit_booking(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        check_in_date = request.POST.get('check_in_date')
        num_guests = int(request.POST.get('num_guests'))

        product = Product.objects.get(pk=product_id)

        # Attempt to decrease the SKU
        if product.decrease_sku(num_guests):
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
            # Handle the case where there are not enough available SKUs
            return HttpResponseBadRequest("Not enough available SKUs")

    else:
        return render(request, 'booking_form.html')

    


######################################### CHANGE PASSWORD ####################################################

@login_required
def change_password(request):
    
    is_vendor = request.user.groups.filter(name='vendor').exists()
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Your password was successfully changed!')
            if is_vendor:
                return redirect('vendor_settings')
            else:
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
        
    return render(request, 'change_password.html', {'form': form, 'is_vendor': is_vendor})



@login_required(login_url='login')
def delete_account(request):
    is_vendor = request.user.groups.filter(name='vendor').exists()
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        if is_vendor:
            return redirect('index')
        else:
            return redirect('index')  
    return render(request, 'delete_account.html', {'is_vendor': is_vendor})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            email = form.cleaned_data['email']
            if email != request.user.email and User.objects.filter(email=email).exists():
                messages.error(request, 'This email address is already associated with another account.')
            else:
                form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('settings')  
        else:
            messages.error(request, 'Error updating profile. Please correct the errors below.')
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form})


def checkout(request):
    return render(request, 'checkout.html')

def customize(request):
    return render(request,'customize.html')















######################################################################## SIGNUP ###############################################################################

import random
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import OTP

# Function to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Function to send OTP via email
def send_otp_email(user, otp):
    subject = 'Email Verification OTP'
    message = f'Your OTP for email verification is: {otp}'
    email_from = 'np03cs3s220121@heraldcollege.edu.np'
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)

# Registration view with email verification
def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            # Extract form data
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
                    # Generate OTP
                    otp = generate_otp()
                    # Create user
                    user = User.objects.create_user(username=username, password=password1, email=email, last_name=last_name, first_name=first_name)
                    # Create OTP instance and associate with user
                    otp_instance = OTP.objects.create(user=user, otp_code=otp)
                    # Send OTP via email
                    send_otp_email(user, otp)
                    messages.success(request, 'Account created successfully.')
                    request.session['username'] = username  # Store username in session for verification
                    return redirect('verify_email')  # Redirect to the OTP verification page
            else:
                messages.error(request, 'Password does not match ')
                return redirect('register')

        else:
            return render(request, 'register.html')

# Verification view
def verify_email(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        if 'username' in request.session:
            username = request.session['username']
            try:
                user = User.objects.get(username=username)
                otp_instance = OTP.objects.get(user=user)
                if otp_instance.otp_code == otp_entered:
                    # Mark OTP as verified
                    otp_instance.verified = True
                    otp_instance.save()
                    # Mark email as verified
                    user.email_verified = True
                    user.save()
                    # Set session variable to indicate email verification
                    request.session['email_verified'] = True
                    messages.success(request, 'Email verified successfully.')
                    del request.session['username']  # Remove username from session
                    return redirect('login')
                else:
                    messages.error(request, 'Invalid OTP. Please try again.')
                    return redirect('verify_email')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('register')  # Redirect to registration page if user not found
            except OTP.DoesNotExist:
                messages.error(request, 'OTP not found.')
                return redirect('register')  # Redirect to registration page if OTP not found
        else:
            messages.error(request, 'Username session not found.')
            return redirect('register')  # Redirect to registration page if username session not found
    else:
        return render(request, 'verify_email.html')

# Login view
def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                try:
                    otp_instance = OTP.objects.get(user=user)
                    if not otp_instance.verified:
                        # Redirect to OTP verification page if OTP is not verified
                        request.session['username'] = username
                        return redirect('verify_email')
                except OTP.DoesNotExist:
                    # If OTP instance does not exist, redirect to OTP verification page
                    request.session['username'] = username
                    return redirect('verify_email')
                
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
    # Fetch the number of products added by the vendor
    num_products = Product.objects.filter(user=request.user).count()
    
    # Fetch the number of bookings received by the vendor
    num_bookings = Booking.objects.filter(product__user=request.user).count()
    
    context = {
        'num_products': num_products,
        'num_bookings': num_bookings
    }
    
    return render(request, 'vendor_dashboard.html', context)


def vendor_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.groups.filter(name='vendor').exists():
            try:
                otp_instance = OTP.objects.get(user=user)
                if not otp_instance.verified:
                    # Redirect to OTP verification page if OTP is not verified
                    request.session['username'] = username
                    return redirect('verify_email')
            except OTP.DoesNotExist:
                # If OTP instance does not exist, redirect to OTP verification page
                request.session['username'] = username
                return redirect('verify_email')
            
            # If OTP is verified or not required, log in the user
            auth_login(request, user)  
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
                vendor_group = Group.objects.get(name='vendor')
                user.groups.add(vendor_group)  # Add user to the vendor group

                # Generate OTP
                otp = generate_otp()
                # Create OTP instance and associate with user
                otp_instance = OTP.objects.create(user=user, otp_code=otp)
                # Send OTP via email
                send_otp_email(user, otp)

                messages.success(request, 'Registration successful. Please verify your email to complete the registration process.')
                request.session['username'] = username  # Store username in session for verification
                return redirect('verify_email')  # Redirect to the OTP verification page
        else:
            messages.error(request, 'Password does not match ')
            return redirect('vendor_register')

    else:
        return render(request, 'vendor_register.html')

######################################################################## ADD PRODUCT ###############################################################################
from .forms import AddProductForm, AddProductFormSet,ProductImageForm
from django.forms import inlineformset_factory
@vendor_only


@vendor_only
def add_product(request):
    ImageFormSet = inlineformset_factory(Product, ProductImages, form=ProductImageForm, extra=3)

    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        formset = ImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            form.save_m2m()
            formset.instance = new_form  # Link formset to the new product instance
            formset.save()
            messages.success(request, "Product added successfully.")
            return redirect("vendor_dashboard")  
    else:
        form = AddProductForm()
        formset = ImageFormSet()

    context = {
        "form": form,
        "formset": formset,  # Pass formset to template context
    }

    return render(request, "vendor_add_product.html", context)


########################################Vendor Products##########################################
@vendor_only
def vendor_products(request):
    current_user = request.user
    
    all_products = Product.objects.filter(user=current_user)
    
    context = {
        "all_products": all_products,
    }

    return render(request, "vendor_products.html", context)

####################################### EDIT PRODUCT ################################################

@vendor_only
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            edited_product = form.save(commit=False)
            edited_product.user = request.user
            edited_product.save()
            form.save_m2m()
            messages.success(request, "Product updated successfully.")
            return redirect("vendor_products")
    else:
        form = AddProductForm(instance=product)

    context = {
        "form": form,
        "product": product,
    }

    return render(request, "vendor_edit_product.html", context)


####################################### DELETE PRODUCT ################################################
@vendor_only
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('vendor_products')
    return render(request, 'vendor_delete_product.html', {'product': product})


def vendor_settings(request):

    return render(request,"vendor_settings.html")


def vendor_edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            email = form.cleaned_data['email']
            if email != request.user.email and User.objects.filter(email=email).exists():
                messages.error(request, 'This email address is already associated with another account.')
            else:
                form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('vendor_settings')  
        else:
            messages.error(request, 'Error updating profile. Please correct the errors below.')
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'vendor_edit_profile.html', {'form': form})















########################################################### Forget Password #################################################################3


class ForgotPasswordView(FormView):
    template_name = 'forgot_password.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        site = get_current_site(self.request)
        domain = site.domain
        protocol = 'http' if self.request.is_secure() else 'https'
        
        form.save(
            request=self.request,
            from_email='example@example.com',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt',
            extra_email_context={
                'domain': domain,
                'protocol': protocol,
            }
        )
        
        return super().form_valid(form)


class CustomPasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    template_name = 'password_reset_form.html'


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('password_reset_complete')
    template_name = 'password_reset_confirm.html'


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
