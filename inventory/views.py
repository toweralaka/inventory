from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate


# Create your views here.


def home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    else:
        return render(request, 'index.html')