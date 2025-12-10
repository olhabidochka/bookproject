

from bookstore.models import Book
from django.contrib.auth.models import User
from django.urls import reverse
from bookstore.models import Book, Author, Publisher, Genre, Cart



@pytest.fixture
def user(db):

    return User.objects.create_user(
        username='testuser',
        email='test@test.com',
        password='testpass123'
    )


@pytest.fixture
def staff_user(db):

    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='admin123',
        is_staff=True
    )


@pytest.fixture
def genre(db):

    return Genre.objects.create(name='Фантастика', slug='fantasy')


@pytest.fixture
def publisher(db):

    return Publisher.objects.create(
        name='Тестове видавництво',
        description='Опис видавництва'
    )


@pytest.fixture
def author(db):

    return Author.objects.create(
        first_name='Тарас',
        last_name='Шевченко'
    )


@pytest.fixture
def book(db, author, publisher, genre):

    book = Book.objects.create(
        title='Тестова книга',
        publisher=publisher,
        isbn='1234567890123',
        description='Опис тестової книги',
        pages=200,
        language='Українська',
        price=100.00,
        discount=0,
        publication_date='2024-01-01',
        stock=10
    )
    book.authors.add(author)
    book.genres.add(genre)
    return book




@pytest.mark.django_db
class TestBookModel:


    def test_book_creation(self, book):

        assert book.title == 'Тестова книга'
        assert book.price == 100.00
        assert book.stock == 10
        assert book.is_available is True

    def test_final_price_without_discount(self, book):

        assert book.final_price == 100.00

    def test_final_price_with_discount(self, book):

        book.discount = 20
        book.save()
        assert book.final_price == 80.00

    def test_book_not_available_when_out_of_stock(self, book):

        book.stock = 0
        book.save()
        assert book.is_available is False




@pytest.mark.django_db
class TestBookListView:


    def test_book_list_view_success(self, client, book):

        url = reverse('bookstore:book_list')
        response = client.get(url)

        assert response.status_code == 200
        assert 'Тестова книга' in response.content.decode()

    def test_book_list_view_empty(self, client):

        url = reverse('bookstore:book_list')
        response = client.get(url)

        assert response.status_code == 200
        assert 'Книги не знайдено' in response.content.decode()

    def test_book_search(self, client, book):

        url = reverse('bookstore:book_list') + '?query=Тестова'
        response = client.get(url)

        assert response.status_code == 200
        assert 'Тестова книга' in response.content.decode()


@pytest.mark.django_db
class TestBookDetailView:


    def test_book_detail_view_success(self, client, book):

        url = reverse('bookstore:book_detail', kwargs={'pk': book.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert 'Тестова книга' in response.content.decode()
        assert '100' in response.content.decode()  # ціна

    def test_book_detail_view_not_found(self, client):

        url = reverse('bookstore:book_detail', kwargs={'pk': 9999})
        response = client.get(url)

        assert response.status_code == 404


@pytest.mark.django_db
class TestBookCreateView:


    def test_create_book_requires_authentication(self, client, author, publisher, genre):

        url = reverse('bookstore:book_create')
        response = client.get(url)


        assert response.status_code == 302
        assert '/login/' in response.url

    def test_create_book_requires_staff(self, client, user, author, publisher, genre):

        client.force_login(user)
        url = reverse('bookstore:book_create')
        response = client.get(url)


        assert response.status_code == 302

    def test_create_book_success(self, client, staff_user, author, publisher, genre):

        client.force_login(staff_user)
        url = reverse('bookstore:book_create')

        data = {
            'title': 'Нова книга',
            'authors': [author.pk],
            'publisher': publisher.pk,
            'genres': [genre.pk],
            'isbn': '9876543210123',
            'description': 'Опис нової книги',
            'pages': 300,
            'language': 'Українська',
            'price': 150.00,
            'discount': 10,
            'publication_date': '2024-06-01',
            'stock': 5
        }

        response = client.post(url, data)


        assert response.status_code == 302

        assert Book.objects.filter(title='Нова книга').exists()

    def test_create_book_invalid_data(self, client, staff_user):

        client.force_login(staff_user)
        url = reverse('bookstore:book_create')


        data = {
            'title': '',
            'price': -10,
        }

        response = client.post(url, data)


        assert response.status_code == 200
        assert Book.objects.filter(title='').count() == 0


@pytest.mark.django_db
class TestBookUpdateView:


    def test_update_book_requires_staff(self, client, user, book):

        client.force_login(user)
        url = reverse('bookstore:book_update', kwargs={'pk': book.pk})
        response = client.get(url)

        assert response.status_code == 302

    def test_update_book_success(self, client, staff_user, book):

        client.force_login(staff_user)
        url = reverse('bookstore:book_update', kwargs={'pk': book.pk})

        data = {
            'title': 'Оновлена назва',
            'authors': [book.authors.first().pk],
            'publisher': book.publisher.pk,
            'genres': [book.genres.first().pk],
            'isbn': book.isbn,
            'description': book.description,
            'pages': book.pages,
            'language': book.language,
            'price': 200.00,
            'discount': book.discount,
            'publication_date': book.publication_date,
            'stock': book.stock
        }

        response = client.post(url, data)


        book.refresh_from_db()

        assert response.status_code == 302
        assert book.title == 'Оновлена назва'
        assert book.price == 200.00

    def test_update_nonexistent_book(self, client, staff_user):

        client.force_login(staff_user)
        url = reverse('bookstore:book_update', kwargs={'pk': 9999})
        response = client.get(url)

        assert response.status_code == 404


@pytest.mark.django_db
class TestBookDeleteView:


    def test_delete_book_requires_staff(self, client, user, book):

        client.force_login(user)
        url = reverse('bookstore:book_delete', kwargs={'pk': book.pk})
        response = client.get(url)

        assert response.status_code == 302

    def test_delete_book_success(self, client, staff_user, book):

        client.force_login(staff_user)
        book_pk = book.pk
        url = reverse('bookstore:book_delete', kwargs={'pk': book_pk})

        response = client.post(url)

        assert response.status_code == 302
        assert not Book.objects.filter(pk=book_pk).exists()

    def test_delete_nonexistent_book(self, client, staff_user):

        client.force_login(staff_user)
        url = reverse('bookstore:book_delete', kwargs={'pk': 9999})
        response = client.get(url)

        assert response.status_code == 404


@pytest.mark.django_db
class TestCartFunctionality:


    def test_add_to_cart_requires_authentication(self, client, book):

        url = reverse('bookstore:add_to_cart', kwargs={'pk': book.pk})
        response = client.get(url)

        assert response.status_code == 302
        assert '/login/' in response.url

    def test_add_to_cart_success(self, client, user, book):

        client.force_login(user)
        url = reverse('bookstore:add_to_cart', kwargs={'pk': book.pk})

        response = client.get(url)


        cart = Cart.objects.get(user=user)
        assert cart.items.count() == 1
        assert cart.items.first().book == book

    def test_add_out_of_stock_book(self, client, user, book):

        book.stock = 0
        book.save()

        client.force_login(user)
        url = reverse('bookstore:add_to_cart', kwargs={'pk': book.pk})

        response = client.get(url, follow=True)


        cart = Cart.objects.get(user=user)
        assert cart.items.count() == 0




@pytest.mark.django_db
class TestUserAuthentication:


    def test_user_registration_success(self, client):

        url = reverse('bookstore:register')

        data = {
            'username': 'newuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'newuser@test.com',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }

        response = client.post(url, data)

        assert response.status_code == 302
        assert User.objects.filter(username='newuser').exists()

    def test_user_login_success(self, client, user):

        url = reverse('bookstore:login')

        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = client.post(url, data)

        assert response.status_code == 302

    def test_user_login_invalid_credentials(self, client):

        url = reverse('bookstore:login')

        data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }

        response = client.post(url, data)


        assert response.status_code == 200