from django.shortcuts import render, redirect

# Create your views here.

def index(request):
    return render(request, 'index.html')

def register_page(request):
    return redirect('login')

def login_page(request):
    return render(request, 'login.html')
