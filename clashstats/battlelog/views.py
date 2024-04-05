from django.shortcuts import render
from clashstats.battlelog.api import get_battlelog

# Create your views here.
def home(request):
    return render(request, 'home.html')

def battlelog(request, tag):
    return render(request, 'battlelog.html', json = get_battlelog(tag))
