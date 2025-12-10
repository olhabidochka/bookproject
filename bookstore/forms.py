from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Book, Author, Publisher, Genre, UserProfile, Order


class UserRegistrationForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Ім'я"
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Прізвище'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Ім'я користувача"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Підтвердіть пароль'
        })


class UserLoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Ім'я користувача"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'postal_code', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+380...'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Вулиця, будинок, квартира'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Місто'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
        }


class BookForm(forms.ModelForm):

    class Meta:
        model = Book
        fields = [
            'title', 'authors', 'publisher', 'genres', 'isbn',
            'description', 'pages', 'language', 'price', 'discount',
            'cover_image', 'publication_date', 'stock'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Назва книги'
            }),
            'authors': forms.SelectMultiple(attrs={
                'class': 'form-control'
            }),
            'publisher': forms.Select(attrs={
                'class': 'form-control'
            }),
            'genres': forms.SelectMultiple(attrs={
                'class': 'form-control'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '978-...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опис книги'
            }),
            'pages': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'language': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Українська'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'publication_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }


class AuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'bio', 'photo', 'birth_date']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Ім'я"
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Прізвище'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Біографія автора'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class PublisherForm(forms.ModelForm):

    class Meta:
        model = Publisher
        fields = ['name', 'description', 'website', 'email', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Назва видавництва'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опис видавництва'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://...'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


class BookSearchForm(forms.Form):

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пошук за назвою або автором...'
        })
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label="Всі жанри",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        empty_label="Всі видавництва",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'За замовчуванням'),
            ('price_asc', 'Від дешевих до дорогих'),
            ('price_desc', 'Від дорогих до дешевих'),
            ('popularity', 'За популярністю'),
            ('title', 'За назвою'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class CheckoutForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['delivery_address', 'delivery_city', 'delivery_postal_code', 'phone', 'notes']
        widgets = {
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Вулиця, будинок, квартира'
            }),
            'delivery_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Місто'
            }),
            'delivery_postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+380...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Додаткова інформація (необов\'язково)'
            }),
        }