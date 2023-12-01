from django.contrib import admin
from .models import *
# Register your models here.

class StorageInlineAdmin(admin.TabularInline):
    
    model = Storage
    extra = 0

class ProductInlineAdmin(admin.TabularInline):
    
    model = Product
    extra = 0

class ServiceInputInlineAdmin(admin.TabularInline):

    model = ServiceInput
    extra = 0

class ServiceOutputInlineAdmin(admin.TabularInline):

    model = ServiceOutput
    extra = 0

class DocumentInputAdmin(admin.ModelAdmin):
    
    model = DocumentInput
    inlines = [ProductInlineAdmin, ServiceInputInlineAdmin]

class DocumentOutputAdmin(admin.ModelAdmin):

    model = DocumentOutput
    inlines = [ProductInlineAdmin,  ServiceOutputInlineAdmin]

admin.site.register(DocumentInput, DocumentInputAdmin)
admin.site.register(DocumentOutput, DocumentOutputAdmin)
admin.site.register(Product)
admin.site.register(Storage)
admin.site.register(ServiceInput)
admin.site.register(ServiceOutput)