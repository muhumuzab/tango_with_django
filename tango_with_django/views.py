from django.shortcuts import render
#views.py

def index(request):
    return render(request, "index.html")

def about(request):
    return render(request,"about.html")
