from django.contrib import admin
from .models import Book, Genre, MyProfile, Review
# Register your models here.

admin.site.register(Book)
admin.site.register(Genre)
admin.site.register(MyProfile)
admin.site.register(Review)
