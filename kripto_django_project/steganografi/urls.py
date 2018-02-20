from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url('old', views.index_jelek, name='index_jelek'),
    url('result', views.result, name='result'),
    url('extract', views.extract, name='extract'),
    url('extract/result', views.extract_result, name='extract_result'),
]