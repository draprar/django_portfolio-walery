from django.shortcuts import render
from analytics.utils import count_visit

@count_visit
def index(request):
    return render(request, 'bies/index.html')
