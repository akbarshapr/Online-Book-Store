from django.urls import path
from .views import HomePageView, BookList, BookDetail, MyProfileView, MyProfileCreate

urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'),
    path('booklist/', BookList.as_view(), name='books'),
    path('bookdetail/<int:pk>', BookDetail.as_view(), name='bookdetail'),

    path('myprofile/', MyProfileView.as_view(), name='myprofile'),
    path('createprofile/', MyProfileCreate.as_view(), name='createprofile'),

]
