# events/urls.py

from django.urls import path

from events import views

urlpatterns = [
    path('events/', views.event_list, name='event_list'),
]
