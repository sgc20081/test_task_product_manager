from django import forms
from .models import *

class DocumentInputForm(forms.ModelForm):

    class Meta:
        model = DocumentInput
        fields = '__all__'

class DocumentOutputForm(forms.ModelForm):

    class Meta:
        model = DocumentOutput
        fields = '__all__'

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'
        # exclude = ['balance']

# class ProductBalanceForm(forms.ModelForm):

#     class Meta:
#         model = ProductBalance
#         fields = '__all__'

class ServiceInputForm(forms.ModelForm):

    class Meta:
        model = ServiceInput
        fields = '__all__'

class ServiceOutputForm(forms.ModelForm):

    class Meta:
        model = ServiceOutput
        fields = '__all__'