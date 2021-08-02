from . import views
from django.urls import path

urlpatterns = [
    path('', views.ShowCardGameHome, name='showcardgamehome'),
    path('room/<str:room_name>/<str:person_name>', views.ShowCardGamePage, name='showcardgamepage')
]
