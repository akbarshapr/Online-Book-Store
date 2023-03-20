from .models import Book, MyProfile

from django.views.generic import TemplateView
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Create your views here.


class HomePageView(TemplateView):
    template_name = 'main/home.html'


class BookList(LoginRequiredMixin, ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'book/booklist.html'


class BookDetail(LoginRequiredMixin, DetailView):
    model = Book
    context_object_name = 'books'
    template_name = 'book/bookdetail.html'


class MyProfileView(LoginRequiredMixin, ListView):
    model = MyProfile
    context_object_name = 'myprofile'
    template_name = 'book/my_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myprofile'] = context['myprofile'].filter(user=self.request.user)
        return context


class MyProfileCreate(LoginRequiredMixin, CreateView):
    model = MyProfile
    fields = ['name', 'email', 'pfp', 'bio', 'favorites', 'delivery_address']
    success_url = reverse_lazy('myprofile')
    template_name = 'book/create_profile.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(MyProfileCreate, self).form_valid(form)
