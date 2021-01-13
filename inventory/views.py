from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate


# Create your views here.
# def user_login(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         # Redirect to a success page.
#         ...
#     else:
#         # Return an 'invalid login' error message.
#         ...


def home(request):
    return render(request, 'index.html')