from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.views.generic import TemplateView
from bpcs import BPCS
import os
from django.conf import settings
# from django.conf.settings import MEDIA_ROOT
from django.core.files.storage import FileSystemStorage

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

    # handle FILES
    # handle image
    image = request.FILES['image_path']
    fs = FileSystemStorage()
    image_name = fs.save(image.name, image)
    image_url = fs.url(image_name)

    # handle "soon to be embeded" file
    file = request.FILES['file_path']
    fs = FileSystemStorage()
    file_name = fs.save(file.name, file)
    file_url = fs.url(file_name)

    bpcs = BPCS(os.path.join(settings.MEDIA_ROOT, image_name), os.path.join(settings.MEDIA_ROOT, file_name))
    bpcs.dividePixels()
    bpcs.createBitplanes()
    bpcs.readMsg()
    bpcs.setStegoKey(key)
    bpcs.encryptMsg()
    bpcs.divideMessage()
    bpcs.createMsgBitplane()
    bpcs.embedding()

    bpcs.createImage()

    bpcs.writeImage()

    stego_name = 'stego_' + image_name
    stego_url = "/media/" + stego_name

    context = {'image_name' : image_name, 'image_url' : image_url, 'stego_name' : stego_name, 'stego_url' : stego_url, 'key' : key, 'threshold' : threshold, 'encrypt' : encrypt, 'random' : random, 'convert_cgc' : convert_cgc}
    return HttpResponse(template.render(context,request))