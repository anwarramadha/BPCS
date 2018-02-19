from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.views.generic import TemplateView
import os

def index(request):
    module_dir = os.path.dirname(__file__)
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

def index_jelek(request):
    module_dir = os.path.dirname(__file__)
    template = loader.get_template('index_jelek.html')
    return HttpResponse(template.render({}, request))

def result(request):
    # print(restaurantRatingSystem.main_sentiment)
    # print(restaurantRatingSystem.find_rating('KFC'))
    template = loader.get_template('result.html')
    filepath = request.POST.get('filepath', '')
    key = request.POST.get('key', '')
    threshold = request.POST.get('threshold', '')
    encrypt = False
    if request.method == 'POST' and 'encrypt' in request.GET:
    	encrypt = True
    random = False
    if request.method == 'POST' and 'random' in request.GET:
    	random = True
    convert_cgc = False
    if request.method == 'POST' and 'convert-cgc' in request.GET:
    	convert_cgc = request.POST.get('convert_cgc', '')

    context = {'filepath' : filepath, 'key' : key, 'threshold' : threshold, 'encrypt' : encrypt, 'random' : random, 'convert-cgc' : convert_cgc}
    return HttpResponse(template.render(context,request))