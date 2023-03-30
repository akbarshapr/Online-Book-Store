import requests
from django.db.models import Q
from decimal import Decimal
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Book, MyProfile, Cart, CartItem, SiteReview

from django.views.generic import TemplateView
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
# Create your views here.


# Home Page
class HomePageView(TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = SiteReview.objects.count()
        average_rating = SiteReview.objects.all().aggregate(Avg('rating'))['rating__avg'] or 0
        context['average_rating'] = average_rating
        return context


# Book Views
class BookList(LoginRequiredMixin, ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'book/booklist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['books'] = context['books'].filter(
                Q(title__icontains=search_input) | Q(author__icontains=search_input))
        context['search_input'] = search_input
        return context


class BookDetail(LoginRequiredMixin, DetailView):
    model = Book
    context_object_name = 'books'
    template_name = 'book/bookdetail.html'


# favorites
@login_required
def toggle_favorite(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    user_profile = get_object_or_404(MyProfile, user=request.user)
    if book in user_profile.favorites.all():
        user_profile.favorites.remove(book)
    else:
        user_profile.favorites.add(book)
    return redirect('books')


# My Profile
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


class MyProfileUpdate(LoginRequiredMixin, UpdateView):
    model = MyProfile
    fields = ['name', 'email', 'pfp', 'bio', 'favorites', 'delivery_address']
    success_url = reverse_lazy('myprofile')
    template_name = 'book/create_profile.html'

    def get_object(self, queryset=None):
        return MyProfile.objects.get(user=self.request.user)


# CART
@login_required
def cart(request):
    cart_qs = Cart.objects.filter(user=request.user)
    if cart_qs.exists():
        cart_obj = cart_qs.first()
        cart_items = CartItem.objects.filter(cart=cart_obj)
    else:
        cart_obj = None
        cart_items = []

    context = {
        'cart': cart_obj,
        'cart_items': cart_items
    }
    return render(request, 'cart/mycart.html', context)


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart_qs = Cart.objects.filter(user=request.user)
    if cart_qs.exists():
        cart_obj = cart_qs.first()
    else:
        cart_obj = Cart.objects.create(user=request.user, total_price=Decimal('0.00'))
    cart_item, created = CartItem.objects.get_or_create(book=book, cart=cart_obj)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    cart_obj.total_price += Decimal(str(book.price))
    cart_obj.save()
    return redirect('mycart')


@login_required
def remove_from_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart_qs = Cart.objects.filter(user=request.user)
    if cart_qs.exists():
        cart_obj = cart_qs.first()
        cart_item_qs = CartItem.objects.filter(book=book, cart=cart_obj)
        if cart_item_qs.exists():
            cart_item = cart_item_qs.first()
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
            cart_obj.total_price -= Decimal(str(book.price))
            cart_obj.save()
    return redirect('mycart')


# Site Reviews
class SiteReviewView(ListView):
    model = SiteReview
    context_object_name = 'reviews'
    template_name = 'main/review.html'


class SiteReviewCreate(LoginRequiredMixin, CreateView):
    model = SiteReview
    context_object_name = 'reviewcreate'
    fields = ['review', 'rating']
    template_name = 'main/create-review.html'
    success_url = reverse_lazy('reviews')

    def form_valid(self, form):
        form.instance.user = self.request.user
        myprofile = MyProfile.objects.get(user=self.request.user)
        form.instance.name = myprofile
        return super().form_valid(form)


class SiteReviewDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = SiteReview
    fields = '__all__'
    template_name = 'main/review.html'
    success_url = reverse_lazy('reviews')

    def test_func(self):
        review = self.get_object()
        return review.user == self.request.user


class SiteReviewUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SiteReview
    fields = ['review', 'rating']
    template_name = 'main/create-review.html'
    success_url = reverse_lazy('reviews')

    def test_func(self):
        review = self.get_object()
        return review.user == self.request.user


def book_recommendations(request, query):
    url = f"https://openlibrary.org/search.json?q={query}&limit=10"
    response = requests.get(url)
    data = response.json()
    books = data.get('docs')

    fallback_cover_url = '/static/images/fallback-cover.jpg'  # Change this to the path of your fallback image

    for book in books:
        if 'cover_i' in book:
            book['cover_url'] = f"http://covers.openlibrary.org/b/id/{book['cover_i']}-M.jpg"
        elif 'edition_key' in book:
            book['cover_url'] = f"http://covers.openlibrary.org/b/olid/{book['edition_key'][0]}-M.jpg"
        else:
            book['cover_url'] = fallback_cover_url

    context = {'books': books}
    return render(request, 'book/recommendations.html', context)
