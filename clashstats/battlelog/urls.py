from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("battlelog/<slug:tag>", views.battlelog, name="battlelog"),
    path("playerstatssearch", views.playerstatssearch, name="playerstatssearch"),
]
