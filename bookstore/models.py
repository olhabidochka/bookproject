from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Author(models.Model):

    first_name = models.CharField(blank=True, max_length=100, verbose_name="Ім'я")
    last_name = models.CharField(blank=True,  max_length=100, verbose_name="Прізвище")
    bio = models.TextField(blank=True, verbose_name="Біографія")
    photo = models.ImageField(upload_to='authors/', blank=True, null=True, verbose_name="Фото")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата народження")

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Автори"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Publisher(models.Model):

    name = models.CharField(max_length=200, unique=True, verbose_name="Назва")
    description = models.TextField(blank=True, verbose_name="Опис")
    website = models.URLField(blank=True, verbose_name="Веб-сайт")
    email = models.EmailField(blank=True, verbose_name="Email")
    logo = models.ImageField(upload_to='publishers/', blank=True, null=True, verbose_name="Логотип")

    class Meta:
        verbose_name = "Видавництво"
        verbose_name_plural = "Видавництва"
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):

    name = models.CharField(max_length=100, unique=True, verbose_name="Назва")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Опис")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанри"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Book(models.Model):

    title = models.CharField(max_length=300, verbose_name="Назва")
    authors = models.ManyToManyField(Author, related_name='books', verbose_name="Автори")
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True,
                                  related_name='books', verbose_name="Видавництво")
    genres = models.ManyToManyField(Genre, related_name='books', verbose_name="Жанри")

    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True, verbose_name="ISBN")
    description = models.TextField(verbose_name="Опис")
    pages = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Кількість сторінок")
    language = models.CharField(max_length=50, default="Українська", verbose_name="Мова")

    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)], verbose_name="Ціна")
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0)],
                                   verbose_name="Знижка (%)")

    cover_image = models.ImageField(upload_to='books/covers/', blank=True, null=True,
                                    verbose_name="Обкладинка")
    publication_date = models.DateField(verbose_name="Дата публікації")

    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)],
                                verbose_name="Кількість на складі")
    views = models.IntegerField(default=0, verbose_name="Перегляди")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def final_price(self):

        if self.discount > 0:
            return self.price * (1 - self.discount / 100)
        return self.price

    @property
    def is_available(self):

        return self.stock > 0

    def get_authors_display(self):

        return ", ".join([author.get_full_name() for author in self.authors.all()])


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    address = models.TextField(blank=True, verbose_name="Адреса")
    city = models.CharField(max_length=100, blank=True, verbose_name="Місто")
    postal_code = models.CharField(max_length=10, blank=True, verbose_name="Поштовий індекс")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")

    class Meta:
        verbose_name = "Профіль користувача"
        verbose_name_plural = "Профілі користувачів"

    def __str__(self):
        return f"Профіль {self.user.username}"


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Очікується'),
        ('processing', 'В обробці'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders',
                             verbose_name="Користувач")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending',
                              verbose_name="Статус")

    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Загальна сума")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")


    delivery_address = models.TextField(verbose_name="Адреса доставки")
    delivery_city = models.CharField(max_length=100, verbose_name="Місто")
    delivery_postal_code = models.CharField(max_length=10, verbose_name="Поштовий індекс")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    notes = models.TextField(blank=True, verbose_name="Примітки")

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ['-created_at']

    def __str__(self):
        return f"Замовлення #{self.id} від {self.user.username}"


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items',
                              verbose_name="Замовлення")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Кількість")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")

    class Meta:
        verbose_name = "Елемент замовлення"
        verbose_name_plural = "Елементи замовлення"

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    @property
    def total_price(self):
        return self.price * self.quantity


class Cart(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart',
                                verbose_name="Користувач")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        verbose_name = "Кошик"
        verbose_name_plural = "Кошики"

    def __str__(self):
        return f"Кошик {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items',
                             verbose_name="Кошик")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1,
                                   verbose_name="Кількість")

    class Meta:
        verbose_name = "Елемент кошика"
        verbose_name_plural = "Елементи кошика"
        unique_together = ('cart', 'book')

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    @property
    def total_price(self):
        return self.book.final_price * self.quantity



