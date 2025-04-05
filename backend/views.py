from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def view(req):
    return render(req,HttpResponse("Hello!"))