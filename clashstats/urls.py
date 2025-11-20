from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('api/v1/clan/search', views.searchClan, name='SearchClan'),
    path('api/v1/members', views.addMembers, name='addMember'),
    path('api/v1/clan', views.addClan, name='addClan'),
    path('api/v1/battlelog', views.addBattleLog, name='addBattleLog'),
    path('api/v1/refreshclan', views.refreshClan, name='refreshClan'),
    path('api/v1/updateelo', views.updateelo, name='updateElo'),
    path('api/v1/updateweeklyelo', views.updateweeklyelo, name='updateWeeklyElo'),
]