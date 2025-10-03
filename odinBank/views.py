from django.shortcuts import render

def home(request):
    return render(request, 'odinBank/home/index.html')
