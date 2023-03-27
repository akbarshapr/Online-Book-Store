from django.db.models import Q
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Book, MyProfile, Cart, CartItem

from django.views.generic import TemplateView
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
# Create your views here.


# Home Page
class HomePageView(TemplateView):
    template_name = 'main/home.html'


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


@login_required
def like_review(request):
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        review.like()
        return redirect('bookdetail', pk=review.book.pk)


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
