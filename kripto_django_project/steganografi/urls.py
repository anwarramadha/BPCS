from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url('old', views.index_jelek, name='index_jelek'),
    url('result', views.result, name='result'),
]