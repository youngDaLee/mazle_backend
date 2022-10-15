from django.urls import path
from .views import SignUp, SignIn, Logout

urlpatterns = [
    path('create/', SignUp.as_view()),
    path('login/', SignIn.as_view()),
    path('logout/', Logout.as_view()),
]