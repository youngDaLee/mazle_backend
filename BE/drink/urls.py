from django.urls import path
from .views import DrinkView, DrinkDetailView, DrinkReviewView, DrinkLikeView

urlpatterns = [
    path('list/', DrinkView.as_view()),
    path('detail/<int:pk>/', DrinkDetailView.as_view()),
    path('review/<int:pk>/', DrinkReviewView.as_view()),
    path('like/<int:pk>/', DrinkLikeView.as_view()),
    # path('like/comment/<int:pk>',DrinkCommentLikeView.as_view()),
]