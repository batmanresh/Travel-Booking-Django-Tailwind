from django.shortcuts import render,redirect
# from .models import destination_preview
# from .models import detailed_desc
# from .models import pessanger_detail
# from .models import Cards
# from .models import Transactions
# from .models import NetBanking
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import *
from django.utils.dateparse import parse_date
from django.views.decorators.cache import cache_control
from django.core.mail import send_mail
from django import forms
from django.forms.formsets import formset_factory
from django.shortcuts import render
from django.template import Library
from datetime import datetime




# Create your views here.
def base(request):
    return render(request, "base.html")

def index(request):
    return render(request, "index.html")

def destination_details(request):
    return render(request, "destination_details.html")

def destination(request):
    return render(request, "destination.html")


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
                messages.info(request, 'Username Taken')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email already Taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, password=password1, email=email, last_name=last_name,
                                                first_name=first_name)
                user.save()
                print('User Created')
                return redirect('login')
        else:
            messages.info(request, 'Password does not match ')
            return redirect('register')

    else:
        return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.info(request, 'Sucessfully Logged in')
            # email = request.user.email
            # print(email)
            # content = 'Hello ' + request.user.first_name + ' ' + request.user.last_name + '\n' + 'You are logged in in our site.keep connected and keep travelling.'
            # send_mail('Alert for Login', content
            #           , 'travellotours89@gmail.com', [email], fail_silently=True)
            # dests = destination_preview.objects.all()
            # return render(request, 'index.html',{'dests':dests})
            return  redirect('index')
        else:
            messages.info(request, 'Invalid credential')
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return redirect('index')

