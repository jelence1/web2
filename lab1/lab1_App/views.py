from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def index(request):
    return render(request, "index.html")

def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    

def signup(request):
    if request.method == "GET":
        return render(request, "signup.html")

def details(request):
    return render(request, "details.html")

def logout(request):
    pass