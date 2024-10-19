from django.urls import path
from userauths import views
from userauths.views import profile_update


app_name = "userauths"

urlpatterns= [
    path("sign-up/", views.register_view, name = "sign-up"),
    path("sign-in/", views.login_view, name = "sign-in"),
    path("sign-out/", views.logout_view, name = "sign-out"),
    path("profile/update/", profile_update, name = "profile-update"),
    
]