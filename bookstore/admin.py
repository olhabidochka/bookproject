from django.contrib import admin
from .models import Author, Publisher, Genre, Book, UserProfile, Order, OrderItem, Cart, CartItem


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'birth_date']
    search_fields = ['first_name', 'last_name']
    list_filter = ['birth_date']


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'email']
    search_fields = ['name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class BookAuthorInline(admin.TabularInline):
    model = Book.authors.through
    extra = 1


class BookGenreInline(admin.TabularInline):
    model = Book.genres.through
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_authors_display', 'publisher', 'price', 'discount',
                    'stock', 'is_available', 'created_at']
    list_filter = ['publisher', 'genres', 'language', 'publication_date']
    search_fields = ['title', 'isbn', 'authors__first_name', 'authors__last_name']
    filter_horizontal = ['authors', 'genres']
    date_hierarchy = 'publication_date'
    readonly_fields = ['views', 'created_at', 'updated_at']

    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'authors', 'publisher', 'genres', 'isbn')
        }),
        ('Опис', {
            'fields': ('description', 'cover_image')
        }),
        ('Деталі', {
            'fields': ('pages', 'language', 'publication_date')
        }),
        ('Ціна та наявність', {
            'fields': ('price', 'discount', 'stock')
        }),
        ('Статистика', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city']
    search_fields = ['user__username', 'user__email', 'phone']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price', 'total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Інформація про замовлення', {
            'fields': ('user', 'status', 'total_price')
        }),
        ('Доставка', {
            'fields': ('delivery_address', 'delivery_city', 'delivery_postal_code', 'phone')
        }),
        ('Додатково', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'updated_at']
    search_fields = ['user__username']
    inlines = [CartItemInline]



