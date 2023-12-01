from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Storage(models.Model):

    storage = models.CharField(max_length=300)

    def __str__(self):
        return self.storage

class DocumentInput(models.Model):

    date = models.DateTimeField()
    number = models.CharField(max_length=300)

    operation_options = [
        ('option_1', 'Покупка, комісія'),
        ('option_2', 'Об\'єкти будівництва'),
        ('option_2', 'У переробку'),
    ]

    operation = models.CharField(max_length=300, choices=operation_options)
    sum = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=300)
    contractor = models.CharField(max_length=300)
    entry_date = models.DateTimeField(null=True, blank=True)
    entry_number = models.CharField(max_length=300, null=True, blank=True)
    contract = models.CharField(max_length=300)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='document_input', null=True)

    def __str__(self):
        return self.number

class DocumentOutput(models.Model):

    date = models.DateTimeField()
    number = models.CharField(max_length=300)
    operation = models.CharField(max_length=300)
    sum = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=300)
    organization = models.CharField(max_length=300)
    contract = models.CharField(max_length=300, null=True)
    accountable = models.CharField(max_length=300)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='document_output', null=True)

    def __str__(self):
        return self.number

class Product(models.Model):

    nomenclature = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    units = models.CharField(max_length=300)
    coefficient = models.DecimalField(max_digits=15, decimal_places=3)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=3, decimal_places=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    bill = models.IntegerField()
    balance = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    product_index = models.CharField(max_length=30, null=True)
    document_product_input = models.ForeignKey(DocumentInput, related_name='product', on_delete=models.CASCADE, null=True, blank=True)
    document_product_output = models.ForeignKey(DocumentOutput, related_name='product', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nomenclature   

class ServiceInput(models.Model):

    nomenclature = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=3, decimal_places=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    bill = models.IntegerField()
    sub_account = models.CharField(max_length=300)
    document_service_input = models.ForeignKey(DocumentInput, related_name='service_input', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nomenclature
    
class ServiceOutput(models.Model):

    nomenclature = models.CharField(max_length=300)
    description = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    # tax_rate = models.DecimalField(max_digits=3, decimal_places=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    discount = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    bill = models.IntegerField(null=True)
    document_service_output = models.ForeignKey(DocumentOutput, related_name='service_output', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nomenclature