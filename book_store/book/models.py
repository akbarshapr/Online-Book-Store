from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default="#000000")

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField(null=True, blank=True)
    image_url = models.CharField(max_length=2083, blank=True)
    follow_author = models.CharField(max_length=2083, blank=True)
    book_available = models.BooleanField()
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return self.title


class MyProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    pfp = models.ImageField(upload_to='profiles', null=True, blank=True, height_field=None, width_field=None,
                            max_length=None)
    bio = models.CharField(max_length=200)
    favorites = models.ManyToManyField(Book)
    delivery_address = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
