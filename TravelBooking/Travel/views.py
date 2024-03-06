from django.shortcuts import render

from django.http import HttpResponse

def Travel(request):
    return render(request,'Travel/index.html')
# Create your views here.
