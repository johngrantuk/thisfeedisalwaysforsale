from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('decrypt/', views.decrypt, name='decrypt'),
    path('feed_admin/', views.feed_admin, name='feed_admin'),
    path('feed_admin/create_policy/', views.create_policy, name='create_policy'),
    path('feed_admin/add_post/', views.add_post, name='add_post')
]
