from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from userauths.forms import UserRegisterForm , ProfileForm
from userauths.models import Profile


def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, Your account was created successfully")
            login(request, new_user)
            return redirect("core:index")
    else:
        form = UserRegisterForm()
    context = {'form': form}
    return render(request, "userauths/sign-up.html", context)

def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("core:index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        authenticated_user = authenticate(request, email=email, password=password)

        if authenticated_user is not None:
            login(request, authenticated_user)
            messages.success(request, "You are logged in.")
            return redirect("core:index")
        else:
            messages.warning(request, "User does not exist or incorrect password.")
            messages.warning(request, "Or create an account.")

    return render(request, "userauths/sign-in.html", {})

def logout_view(request):
    print("logout called")
    logout(request)
    messages.success(request, "You are logged out.")
    return redirect("userauths:sign-in")

def profile_update(request):
    profile = Profile.objects.get(user=request.user)
    if request.method =="POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("core:dashboard")
    else:
        form= ProfileForm(instance=profile)        
   

    context ={
        "form":form,
        "profile":profile,
    }

    return render(request, "userauths/profile-edit.html",context)    
