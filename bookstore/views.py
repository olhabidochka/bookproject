from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import (
    Book, Author, Publisher, Genre, UserProfile,
    Cart, CartItem, Order, OrderItem
)
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm,
    UserUpdateForm, BookForm, AuthorForm, PublisherForm,
    BookSearchForm, CheckoutForm
)


def index(request):

    featured_books = Book.objects.filter(stock__gt=0).order_by('-views')[:8]
    new_books = Book.objects.filter(stock__gt=0).order_by('-created_at')[:8]
    popular_genres = Genre.objects.annotate(book_count=Count('books')).order_by('-book_count')[:6]

    context = {
        'featured_books': featured_books,
        'new_books': new_books,
        'popular_genres': popular_genres,
    }
    return render(request, 'bookstore/index.html', context)



def book_list(request):

    books = Book.objects.filter(stock__gt=0).select_related('publisher').prefetch_related('authors', 'genres')


    query = request.GET.get('query', '')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(authors__first_name__icontains=query) |
            Q(authors__last_name__icontains=query) |
            Q(isbn__icontains=query)
        ).distinct()


    genre_id = request.GET.get('genre')
    if genre_id:
        books = books.filter(genres__id=genre_id)


    publisher_id = request.GET.get('publisher')
    if publisher_id:
        books = books.filter(publisher__id=publisher_id)


    sort_by = request.GET.get('sort_by', '')
    if sort_by == 'price_asc':
        books = books.order_by('price')
    elif sort_by == 'price_desc':
        books = books.order_by('-price')
    elif sort_by == 'popularity':
        books = books.order_by('-views')
    elif sort_by == 'title':
        books = books.order_by('title')
    else:
        books = books.order_by('-created_at')


    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    genres = Genre.objects.all()
    publishers = Publisher.objects.all()

    context = {
        'page_obj': page_obj,
        'genres': genres,
        'publishers': publishers,
        'query': query,
        'selected_genre': genre_id,
        'selected_publisher': publisher_id,
        'sort_by': sort_by,
    }
    return render(request, 'bookstore/book_list.html', context)


def book_detail(request, pk):

    book = get_object_or_404(
        Book.objects.select_related('publisher').prefetch_related('authors', 'genres'),
        pk=pk
    )


    book.views += 1
    book.save(update_fields=['views'])


    related_books = Book.objects.filter(
        genres__in=book.genres.all(),
        stock__gt=0
    ).exclude(pk=book.pk).distinct()[:4]

    context = {
        'book': book,
        'related_books': related_books,
    }
    return render(request, 'bookstore/book_detail.html', context)



def author_list(request):

    authors = Author.objects.annotate(book_count=Count('books')).order_by('last_name')


    query = request.GET.get('query', '')
    if query:
        authors = authors.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )


    paginator = Paginator(authors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'bookstore/author_list.html', context)


def author_detail(request, pk):

    author = get_object_or_404(Author, pk=pk)
    books = Book.objects.filter(authors=author, stock__gt=0).select_related('publisher')

    context = {
        'author': author,
        'books': books,
    }
    return render(request, 'bookstore/author_detail.html', context)



def publisher_list(request):

    publishers = Publisher.objects.annotate(book_count=Count('books')).order_by('name')


    query = request.GET.get('query', '')
    if query:
        publishers = publishers.filter(name__icontains=query)


    paginator = Paginator(publishers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'bookstore/publisher_list.html', context)


def publisher_detail(request, pk):

    publisher = get_object_or_404(Publisher, pk=pk)
    books = Book.objects.filter(publisher=publisher, stock__gt=0).prefetch_related('authors')

    context = {
        'publisher': publisher,
        'books': books,
    }
    return render(request, 'bookstore/publisher_detail.html', context)



def user_register(request):

    if request.user.is_authenticated:
        return redirect('bookstore:index')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            UserProfile.objects.create(user=user)
            Cart.objects.create(user=user)

            login(request, user)
            messages.success(request, 'Реєстрація пройшла успішно!')
            return redirect('bookstore:index')
    else:
        form = UserRegistrationForm()

    return render(request, 'bookstore/register.html', {'form': form})


def user_login(request):

    if request.user.is_authenticated:
        return redirect('bookstore:index')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Вітаємо, {username}!')

                return redirect(request.POST.get('next') or 'bookstore:index')
    else:
        form = UserLoginForm()

    context = {
        'form': form,
        'next': next_url
    }
    return render(request, 'bookstore/login.html', context)


def user_logout(request):

    logout(request)
    messages.info(request, 'Ви успішно вийшли з системи.')
    return redirect('bookstore:index')



@login_required
def profile(request):

    profile, created = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'profile': profile,
        'orders': orders,
    }
    return render(request, 'bookstore/profile.html', context)


@login_required
def profile_edit(request):

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профіль оновлено успішно!')
            return redirect('bookstore:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'bookstore/profile_edit.html', context)


@login_required
def order_detail(request, pk):

    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'bookstore/order_detail.html', {'order': order})


from django.shortcuts import render




@login_required
def cart_view(request):

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('book').all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'bookstore/cart.html', context)


@login_required
def add_to_cart(request, pk):

    book = get_object_or_404(Book, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)

    if book.stock > 0:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

        if not created:
            if cart_item.quantity < book.stock:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, f'Кількість "{book.title}" збільшено.')
            else:
                messages.warning(request, 'Недостатньо товару на складі.')
        else:
            messages.success(request, f'"{book.title}" додано до кошика.')
    else:
        messages.error(request, 'Книга відсутня на складі.')

    return redirect(request.META.get('HTTP_REFERER', 'bookstore:book_list'))


@login_required
def remove_from_cart(request, pk):

    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    book_title = cart_item.book.title
    cart_item.delete()
    messages.info(request, f'"{book_title}" видалено з кошика.')
    return redirect('bookstore:cart')


@login_required
def update_cart_item(request, pk):

    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))

        if quantity > 0 and quantity <= cart_item.book.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Кількість оновлено.')
        elif quantity > cart_item.book.stock:
            messages.warning(request, 'Недостатньо товару на складі.')
        else:
            cart_item.delete()
            messages.info(request, 'Товар видалено з кошика.')

    return redirect('bookstore:cart')



@login_required
def checkout(request):

    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related('book').all()

    if not cart_items:
        messages.warning(request, 'Ваш кошик порожній.')
        return redirect('bookstore:cart')


    for item in cart_items:
        if item.quantity > item.book.stock:
            messages.error(request, f'Недостатньо "{item.book.title}" на складі.')
            return redirect('bookstore:cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():

            order = form.save(commit=False)
            order.user = request.user
            order.total_price = cart.total_price
            order.save()


            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    book=item.book,
                    quantity=item.quantity,
                    price=item.book.final_price
                )


                item.book.stock -= item.quantity
                item.book.save()


            cart_items.delete()

            messages.success(request, f'Замовлення #{order.id} успішно створено!')
            return redirect('bookstore:order_detail', pk=order.id)
    else:

        profile = getattr(request.user, 'profile', None)
        initial_data = {}
        if profile:
            initial_data = {
                'delivery_address': profile.address,
                'delivery_city': profile.city,
                'delivery_postal_code': profile.postal_code,
                'phone': profile.phone,
            }
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'bookstore/checkout.html', context)


@login_required
def book_create(request):

    if not request.user.is_staff:
        messages.error(request, 'У вас немає доступу до цієї сторінки.')
        return redirect('bookstore:index')

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Книга "{book.title}" успішно додана.')
            return redirect('bookstore:book_detail', pk=book.pk)
    else:
        form = BookForm()

    return render(request, 'bookstore/book_form.html', {'form': form, 'title': 'Додати книгу'})


@login_required
def book_update(request, pk):

    if not request.user.is_staff:
        messages.error(request, 'У вас немає доступу до цієї сторінки.')
        return redirect('bookstore:index')

    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Книга "{book.title}" оновлена.')
            return redirect('bookstore:book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)

    return render(request, 'bookstore/book_form.html', {'form': form, 'title': 'Редагувати книгу'})


@login_required
def book_delete(request, pk):

    if not request.user.is_staff:
        messages.error(request, 'У вас немає доступу до цієї сторінки.')
        return redirect('bookstore:index')

    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Книга "{title}" видалена.')
        return redirect('bookstore:book_list')

    return render(request, 'bookstore/book_confirm_delete.html', {'book': book})



@login_required
def author_create(request):

    if not request.user.is_staff:
        messages.error(request, 'У вас немає доступу до цієї сторінки.')
        return redirect('bookstore:index')

    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES)
        if form.is_valid():
            author = form.save()
            messages.success(request, f'Автор "{author}" успішно доданий.')
            return redirect('bookstore:author_detail', pk=author.pk)
    else:
        form = AuthorForm()

    return render(request, 'bookstore/author_form.html', {'form': form, 'title': 'Додати автора'})


@login_required
def author_update(request, pk):

    if not request.user.is_staff:
        messages.error(request, 'У вас немає доступу до цієї сторінки.')
        return redirect('bookstore:index')

    author = get_object_or_404(Author, pk=pk)

    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES, instance=author)
        if form.is_valid():
            author = form.save()
            messages.success(request, f'Автор "{author}" оновлений.')
            return redirect('bookstore:author_detail', pk=author.pk)
    else:
        form = AuthorForm(instance=author)

    return render(request, 'bookstore/author_form.html', {'form': form, 'title': 'Редагувати автора'})


@login_required
def author_delete(request, pk):

    if not request.user.is_staff:
        messages.error(request, 'У вас немає доступу до цієї сторінки.')
        return redirect('bookstore:index')

    author = get_object_or_404(Author, pk=pk)

    if request.method == 'POST':
        name = str(author)
        author.delete()
        messages.success(request, f'Автор "{name}" видалений.')
        return redirect('bookstore:author_list')

    return render(request, 'bookstore/author_confirm_delete.html', {'author': author})



@login_required
def publisher_create(request):

    if not request.user.is_staff:
        messages.error(request, 'У вас немає доступу до цієї сторінки.')
        return redirect('bookstore:index')

    if request.method == 'POST':
        form = PublisherForm(request.POST, request.FILES)
        if form.is_valid():
            publisher = form.save()
            messages.success(request, f'Видавництво "{publisher}" успішно додано.')
            return redirect('bookstore:publisher_detail', pk=publisher.pk)
    else:
        form = PublisherForm()

    return render(request, 'bookstore/publisher_form.html', {'form': form, 'title': 'Додати видавництво'})


@login_required
def publisher_update(request, pk):

    if not request.user.is_staff:
        messages.error(request, 'У вас немає доступу до цієї сторінки.')
        return redirect('bookstore:index')

    publisher = get_object_or_404(Publisher, pk=pk)

    if request.method == 'POST':
        form = PublisherForm(request.POST, request.FILES, instance=publisher)
        if form.is_valid():
            publisher = form.save()
            messages.success(request, f'Видавництво "{publisher}" оновлено.')
            return redirect('bookstore:publisher_detail', pk=publisher.pk)
    else:
        form = PublisherForm(instance=publisher)

    return render(request, 'bookstore/publisher_form.html', {'form': form, 'title': 'Редагувати видавництво'})


@login_required
def publisher_delete(request, pk):

    if not request.user.is_staff:
        messages.error(request, 'У вас немає доступу до цієї сторінки.')
        return redirect('bookstore:index')

    publisher = get_object_or_404(Publisher, pk=pk)

    if request.method == 'POST':
        name = str(publisher)
        publisher.delete()
        messages.success(request, f'Видавництво "{name}" видалено.')
        return redirect('bookstore:publisher_list')

    return render(request, 'bookstore/publisher_confirm_delete.html', {'publisher': publisher})



def about(request):

    return render(request, 'bookstore/about.html')
