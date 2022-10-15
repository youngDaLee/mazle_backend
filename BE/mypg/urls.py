from django.urls import path
from .views import MyProfileView, MyReviewView, MyRecipeView
urlpatterns = [
    path('profile/', MyProfileView.as_view()),
    path('review/', MyReviewView.as_view()),
    path('recipe/', MyRecipeView.as_view()),
]