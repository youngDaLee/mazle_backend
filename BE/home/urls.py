from django.urls import path
from .views import HotRecipe, HotDrink, HotReview

urlpatterns = [
    path('hot-recipe/', HotRecipe.as_view()),
    path('hot-drink/', HotDrink.as_view()),
    path('hot-review/', HotReview.as_view()),
]