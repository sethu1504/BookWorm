from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_book, name="search"),
    path('overview/', views.overview, name="overview"),
    path('recommendation/', views.recommendation, name="recommendation"),
    path('authors/', views.authors, name="authors"),
    path('publishers/', views.publishers, name="publishers"),
    path('evaluation/', views.evaluation, name="evaluation"),
    path('search_book', views.search_result, name="create"),
    path('display_recommendations', views.get_recommendations, name="getRecommendations"),
    path('<int:book_id>/', views.book_view, name="create")
]
