from django.urls import path
from .Handlers.auth import *
from .views import *

urlpatterns = [
    path("",view),
    path("signin",signin),
    path("login",login),
    path("logout",logout),
]
