from django.shortcuts import render, get_list_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from axes.models import AccessAttempt
from datetime import timedelta



def login_view(request):
    
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user == None:

            return render(request, 'login.html', {'message': 'Credenciais de acesso inválidos'})

        else:

            login(request, user)
            path = request.POST.get('next')

            if path:
                return redirect(path)

            else:
                return redirect('home')
    else:
        if request.method == "GET" and request.user.is_authenticated:
            return redirect('home')
    return render(request, 'login.html')

@login_required
def logoutUser(request):
    logout(request)
    return redirect("login")