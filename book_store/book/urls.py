from django.urls import path
from .views import HomePageView, BookList, BookDetail, MyProfileView, MyProfileCreate, MyProfileUpdate
from . import views

urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'),
    path('booklist/', BookList.as_view(), name='books'),
    path('bookdetail/<int:pk>', BookDetail.as_view(), name='bookdetail'),

    path('myprofile/', MyProfileView.as_view(), name='myprofile'),
    path('createprofile/', MyProfileCreate.as_view(), name='createprofile'),
    path('editprofile/', MyProfileUpdate.as_view(), name='editprofile'),

    path('like_review/', views.like_review, name='like_review'),

    path('cart/', views.cart, name='mycart'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),

]
