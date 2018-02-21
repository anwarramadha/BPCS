from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.views.generic import TemplateView
from safe_bpcs import BPCS
from ImageComparer import ImageComparer
import os
from django.conf import settings
# from django.conf.settings import MEDIA_ROOT
from django.core.files.storage import FileSystemStorage
from django.http import Http404
from kripto_django_project.celeryapp import app

CONTENT_TYPES = ['png', 'bmp']

def index(request):
    module_dir = os.path.dirname(__file__)
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

def index_jelek(request):
    module_dir = os.path.dirname(__file__)
    template = loader.get_template('index_jelek.html')
    return HttpResponse(template.render({}, request))

@app.task
def result(request):
    # print(restaurantRatingSystem.main_sentiment)
    # print(restaurantRatingSystem.find_rating('KFC'))
    template = loader.get_template('result_new.html')
    error = loader.get_template('error.html')

    key = request.POST.get('key', '')
    threshold = request.POST.get('threshold', '')
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
    content_type = image.content_type.split('/')[1]
    if content_type not in CONTENT_TYPES:
        context = {'message': 'file or image type not supported.'}
        return HttpResponse(error.render(context, request))

    fs = FileSystemStorage()
    image_name = fs.save(image.name, image)
    image_url = fs.url(image_name)

    # handle "soon to be embeded" file
    file = request.FILES['file_path']
    fs = FileSystemStorage()
    file_name = fs.save(file.name, file)
    file_url = fs.url(file_name)
    try:
        bpcs = BPCS(os.path.join(settings.MEDIA_ROOT, image_name), os.path.join(settings.MEDIA_ROOT, file_name))
        bpcs.option(convert_cgc, random)
        bpcs.setThreshold(threshold)
        bpcs.dividePixels()
        bpcs.createBitplanes()
        # bpcs.setThreshold(threshold)
        bpcs.readMsg()
        bpcs.setStegoKey(key)

        if (encrypt):
            bpcs.encryptMsg()
        bpcs.divideMessage()
        bpcs.createMsgBitplane()
        if not bpcs.embedding():
            context = {'message': 'message size bigger than cover image.'}
            return HttpResponse(error.render(context, request))

        bpcs.createImage()

        bpcs.writeImage()

    except Exception as e:
        context = {'message': 'message size bigger than cover image.'}
        return HttpResponse(error.render(context, request))

    stego_name = 'stego_' + image_name
    stego_url = "/media/" + stego_name

    ic = ImageComparer(os.path.join(settings.MEDIA_ROOT, image_name), os.path.join(settings.MEDIA_ROOT, stego_name))
    psnr = '{0:.3g}'.format(ic.getPSNR())

    context = {'image_name' : image_name, 'image_url' : image_url, 'stego_name' : stego_name, 'stego_url' : stego_url, 
    'key' : key, 'threshold' : threshold, 'encrypt' : encrypt, 'random' : random, 'convert_cgc' : convert_cgc, 'psnr':psnr}
    return HttpResponse(template.render(context,request))

def extract(request):
    module_dir = os.path.dirname(__file__)
    template = loader.get_template('extract.html')
    return HttpResponse(template.render({}, request))

@app.task
def getmsg(request):
    module_dir = os.path.dirname(__file__)
    # template = loader.get_template('extract_result.html')
    error = loader.get_template('error.html')
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
    image = request.FILES['image_path']
    fs = FileSystemStorage()
    image_name = fs.save(image.name, image)
    image_url = fs.url(image_name)
    bpcs = BPCS(os.path.join(settings.MEDIA_ROOT, image_name), '')
    bpcs.option(convert_cgc, random)
    bpcs.dividePixels()
    bpcs.createBitplanes()
    bpcs.setStegoKey(key)
    if not bpcs.extracting():
        context = {'message':'message not contain any message.'}
        return HttpResponse(error.render(context, request))
    bpcs.joinMessage()
    if (encrypt):
        bpcs.decryptMsg()
    bpcs.createExtractedFile()
    return download(request, bpcs.fileMsgName)

def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def payload(request):
    module_dir = os.path.dirname(__file__)
    template = loader.get_template('payload.html')
    return HttpResponse(template.render({}, request))

def count(request):
    module_dir = os.path.dirname(__file__)
    template = loader.get_template('payload.html')

    # handle input
    threshold = request.POST.get('threshold', '')
    convert_cgc = False
    if request.method == 'POST' and 'convert_cgc' in request.POST:
        convert_cgc = True

    # handle FILES
    # handle image
    image = request.FILES['image_path']
    fs = FileSystemStorage()
    image_name = fs.save(image.name, image)
    image_url = fs.url(image_name)
    bpcs = BPCS(os.path.join(settings.MEDIA_ROOT, image_name), os.path.join(settings.MEDIA_ROOT, image_name))
    bpcs.option(convert_cgc, True)
    bpcs.dividePixels()
    bpcs.createBitplanes()
    payload = bpcs.payloadByte()


    context = {'image_name' : image_name, 'image_url' : image_url, 'threshold' : threshold,
    'convert_cgc' : convert_cgc, 'payload' : payload}

    return HttpResponse(template.render(context, request))