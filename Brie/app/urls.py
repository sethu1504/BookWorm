from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.list_all, name='list_all'),
    path('search/', views.search_book, name="search"),
    path('search_book', views.search_result, name="create"),
    path('<int:book_id>/', views.book_view, name="create")
]
