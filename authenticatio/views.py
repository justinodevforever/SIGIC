from django.shortcuts import render, get_list_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required


def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(
            username=username,
            password=password
        )

        if user == None:

            return render(request, 'login.html', {'message': 'Credenciais de acesso inválidos'})

        else:

            login(request, user)
            path = request.POST.get('next')

            print(path)

            if path:
                return redirect(path)

            else:
                return redirect('home')

    return render(request, 'login.html')

@login_required
def logoutUser(request):
    logout(request)
    return redirect("login")