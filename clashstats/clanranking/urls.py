"""
URL configuration for clashstats project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("clanranking/<slug:clantag>", views.clanranking, name="clanranking"),
    path("clanrankingsearch", views.clanrankingsearch, name="clanrankingsearch"),
    path("clanrefresh/<slug:clantag>", views.clanrefresh, name="clanrefresh"),
    path("2v2", views.twovtwo, name="2v2"),
    path("battles", views.battles, name="battles"),
]
