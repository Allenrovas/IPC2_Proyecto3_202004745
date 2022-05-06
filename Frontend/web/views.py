from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def ayuda(request):
    return render(request, 'ayuda.html')