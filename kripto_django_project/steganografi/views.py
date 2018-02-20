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
    template = loader.get_template('result_new.html')
    image_path = request.POST.get('image_path', '')
    file_path = request.POST.get('file_path', '')
    key = request.POST.get('key', '')
    threshold = request.POST.get('threshold', '')
    encrypt = False
    if request.method == 'POST' and 'encrypt' in request.POST:
    	encrypt = True
    random = False
    if request.method == 'POST' and 'random' in request.POST:
    	random = True
    convert_cgc = False
    if request.method == 'POST' and 'convert_cgc' in request.POST:
    	convert_cgc = True

    context = {'image_path' : image_path, 'file_path' : file_path, 'key' : key, 'threshold' : threshold, 'encrypt' : encrypt, 'random' : random, 'convert_cgc' : convert_cgc}
    return HttpResponse(template.render(context,request))