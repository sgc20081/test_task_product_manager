from django.urls import path
from django.urls import re_path
from . import views

urlpatterns = [
    path('', views.DocumentInputListView.as_view, name='main'),
    path('document-output', views.DocumentOutputListView.as_view, name='document-output'),
    path('products-balance', views.ProductBalanceView.as_view, name='products-balance'),
    path('create-document-input', views.DocumentInputProductFormView.as_view, name='create-document-input'),
    path('create-document-output', views.DocumentOutputProductFormView.as_view, name='create-document-output'),
    path('multi-form-document-input', views.DocumentInputMultiForms.as_view,),
    path('multi-form-document-output', views.DocumentOutputMultiForms.as_view,),
]

urlpatterns += [
    re_path(r'document_input_view/(?P<pk>\d+)\/?$', views.DocumentInputDetailView.as_view, name='document_input_view'),
    re_path(r'document_output_view/(?P<pk>\d+)\/?$', views.DocumentOutputDetailView.as_view, name='document_output_view')
]