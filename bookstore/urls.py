from django.urls import path
from . import views

app_name = 'bookstore'

urlpatterns = [

    path('', views.index, name='index'),


    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/create/', views.book_create, name='book_create'),
    path('books/<int:pk>/edit/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),


    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),
    path('authors/create/', views.author_create, name='author_create'),
    path('authors/<int:pk>/edit/', views.author_update, name='author_update'),
    path('authors/<int:pk>/delete/', views.author_delete, name='author_delete'),


    path('publishers/', views.publisher_list, name='publisher_list'),
    path('publishers/<int:pk>/', views.publisher_detail, name='publisher_detail'),
    path('publishers/create/', views.publisher_create, name='publisher_create'),
    path('publishers/<int:pk>/edit/', views.publisher_update, name='publisher_update'),
    path('publishers/<int:pk>/delete/', views.publisher_delete, name='publisher_delete'),


    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),


    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),


    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),


    path('about/', views.about, name='about'),
]