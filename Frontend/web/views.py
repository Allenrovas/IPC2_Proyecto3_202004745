from django.shortcuts import render
import requests

endpoint  = 'http://localhost:5000{}'

# Create your views here.
def index(request):
    if request.method == 'GET':
        url= endpoint.format('/Mensajes')
        data = requests.get(url)
        context = {
            'data': data.text
        }
        return render(request, 'index.html', context)
    elif request.method == 'POST':
        url= endpoint.format('/Mensajes')
        data = requests.post(url, json=request.POST)
        context = {
            'data': data.text
        }
        return render(request, 'index.html', context)

def ayuda(request):
    return render(request, 'ayuda.html')