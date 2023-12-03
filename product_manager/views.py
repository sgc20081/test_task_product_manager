from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.http import QueryDict

from django.db import connection
from django.db.models import Q
from django.db.models import Sum

from django.utils.decorators import classonlymethod
import json
import ast
from decimal import Decimal

from .forms import *
from .models import *

from django.apps import apps

from django.middleware.csrf import get_token
# Create your views here.

class ModelsSQLTables:

    tables = {
        ProductForm: ProductForm._meta.model._meta.db_table,
        DocumentInputForm: DocumentInputForm._meta.model._meta.db_table,
        DocumentOutputForm: DocumentOutputForm._meta.model._meta.db_table,
        ServiceInputForm: ServiceInputForm._meta.model._meta.db_table,
        ServiceOutputForm: ServiceOutputForm._meta.model._meta.db_table,
    }

    @classonlymethod
    def sql_post(self, *args, **kwargs):
        
        if 'form' in kwargs:
            table_name = self.tables[kwargs['form']]
        else:
            raise KeyError(f"{self}.sql_post() must contain Form Django object")
        
        if 'fields' in kwargs:
            fields = kwargs['fields']
        else:
            raise KeyError(f"{self}.sql_post() must contain dict 'fields' parameter")

        parametres = self.__sql_make_parametres__(self, form=kwargs['form'], fields=fields)

        sql_fields = parametres['fields']
        sql_values = parametres['values']
        
        sql_query = f"INSERT INTO {table_name} ({sql_fields}) VALUES ({sql_values})"

        with connection.cursor() as cursor:
            cursor.execute(sql_query)

        obj_values = self.__sql_get_last_obj__(self, table_name=table_name)

        object = kwargs['form']._meta.model(**obj_values)
        return object

    def __sql_make_parametres__(self, *args, **kwargs):

        if 'fields' in kwargs and 'form' in kwargs:

            model = kwargs['form']._meta.model
            fields = kwargs['fields']
            sql_fields = None
            sql_values = None

            for field, value in fields.items():
                model_field = model._meta.get_field(field)
                if isinstance(model_field, models.ForeignKey):
                    field = f"{field}_id"

                if sql_fields is None:
                    if isinstance(field, str):
                        if field == 'NULL':
                            sql_fields = f"{field}"
                        else:
                            sql_fields = f"'{field}'"
                    else:
                        sql_fields = str(field)
                else:
                    if isinstance(field, str):
                        if field == 'NULL':
                            sql_fields += f", {field}"
                        else:
                            sql_fields += f", '{field}'"
                    else:
                        sql_fields += f", {str(field)}"

                if sql_values is None:
                    if isinstance(value, str):
                        if value == 'NULL':
                            sql_values = f"{value}"
                        else:
                            sql_values = f"'{value}'"
                    else:
                        sql_values = str(value)
                else:
                    if isinstance(value, str):
                        if value == 'NULL':
                            sql_values += f", {value}"
                        else:
                            sql_values += f", '{value}'"
                    else:
                        sql_values += f", {str(value)}"

            return {'fields': sql_fields, 'values': sql_values}

        else:
            raise KeyError(f"{self}.__sql_make_parametres_() must contain 'fields' and 'form' parametres")
    
    def __sql_get_last_obj__(self, *args, **kwargs):

        if 'table_name' in kwargs:
            table_name = kwargs['table_name']

        sql_query = f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 1"

        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            fields = [field[0] for field in cursor.description]
            return {field: value for field, value in zip(fields, cursor.fetchone())}


"""
product_fields = {'nomenclature': 'Значение 100',
                  'quantity': 1,
                  'units': 'Значение 2',
                  'coefficient': 1,
                  'price': 1,
                  'tax_rate': 1,
                  'bill': 1,
                  'balance': 1,
                  'product_index': 'Значение 3',
                  'document_product_input_id': 1,
                  'document_product_output_id': 'NULL'}
ModelsSQLTables.sql_post(form=ProductForm, fields=product_fields)
"""


class GeneralView:

    model = None
    template = None
    # result = {}

    def __init__(self, *args, **kwargs):
        print('Инициализация базового класса')
        print('Self: ', self)
        print('args: ', args)
        print('kwargs: ', kwargs)
        if args:
            self.request = args[0]
        else:
            self.request = None
        self._response_body = None
        self.result = {}
        
        # csrf_token = get_token(self.request)
        # Выводим токен в консоль
        # print("=======================================CSRF Token:", csrf_token)
        self.ajax = False # на случай, если проверка на ajax понадобиться в дочерних классах
            
    def response(self, *args, **kwargs):
        
        self.ajax = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        print('request: ', self.request)
        print('template: ', self.template)
        print('result: ', self.result)
        # for res in self.result:
        #     print('результат: ', res.document)
        if self.ajax:
            html_render = render(self.request, self.template, self.result)
            self._response_body = JsonResponse({'data': html_render.content.decode('utf-8')})
        else:
            self._response_body = render(self.request, self.template, self.result)
            # raise TypeError(f"<{self.__class__.__name__}> должен обрабатывать запросы типа AJAX")
        return self._response_body

    @classonlymethod
    def as_view(cls, *args, **kwargs):
        self = cls(*args, **kwargs)
        return self.response(*args, **kwargs)

    
class GeneralListView(GeneralView):

    name = None

    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        
        if self.name != None:
            self.__list_name = self.name
        else:
            self.__list_name = self.model.__class__.__name__
        
        self.get_queryset()

    def get_queryset(self, *args, **kwargs):
        if self.model._meta.__class__ == models.options.Options:  # проверка на соответсвие объекта модели django
            self.result[self.__list_name] = self.model.objects.all()
        else:
            raise TypeError(f"<{self.__class__.__name__}> must contain model")
        
    @classonlymethod
    def filter_query(self, *args, **kwargs):
        print('поступил запрос на получение списка с фильтрацией данных ', kwargs)
        if 'filter' in kwargs:
            return self.model.objects.filter(**kwargs['filter'])
    

class GeneralDetailView(GeneralView):

    object_name = None

    def __init__(self, *args, **kwargs):
        print('Запущен класс по получению конкретного объекта')
        super().__init__(*args, **kwargs)
        self.kwargs = kwargs

        self._get_object_name_()
        self.__get_object__()

    def _get_object_name_(self, *args, **kwargs):
        if self.object_name != None:
            self.object_name = self.model.__name__
        else:
            self.object_name = self.object

    def __get_object__(self, *args, **kwargs):
        if 'pk' in self.kwargs:
            self.result[self.object_name] = self.model.objects.get(id=self.kwargs['pk'])
        else:
            raise KeyError(f"<{self.__class__.__name__}>: expected a primary key or slug parameter, but got None")
        
class GeneralFormView(GeneralView):

    form = None
    name = None

    __form_key = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__get_request_method__(*args, **kwargs)

    def __get_request_method__(self, *args, **kwargs):
        print('ЗАПУЩЕН КЛАСС ПОЛУЧЕНИЯ ФОРМЫ', self)
        if self.name != None:
            self.__form_key = self.name
        else:
            self.__form_key = self.form.__class__.__name__

        if self.request != None:
            if self.request.method == 'POST':
                self.post()
            elif self.request.method == 'GET':
                if 'pk' in kwargs:
                    self.__object = self.form._meta.model.objects.get(id=kwargs['pk'])
                    self.__get_update_form__()
                else:
                    self.__get__()

    def __get__(self, *args, **kwargs):
        self.result[self.__form_key] = self.form()

    def __get_update_form__(self, *args, **kwargs):
        self.result[self.__form_key] = self.form(instance=self.__object)
    
    # @classonlymethod
    def post(self, *args, **kwargs):
        print('Kwargs в методе post: ', kwargs)
        if 'form' in kwargs:
            print('Прилетела форма: ', kwargs['form'])
            form = kwargs['form'](data=kwargs['initial'])
        else:
            form = self.form(self.request.POST)
            for field, value in form.cleaned_data.items():
                print(f"Поле: {field}, значение: {value}")
        
        print('Это форма, на обработку в POST запросе: ', form)
        
        if form.is_valid():
            if 'get_object' in kwargs:
                print('Получен запрос на возвращаемый объект')
                if kwargs['get_object']:
                    new_object = form.save()
                    print('Возвращаемый объект: ', new_object)
                    return new_object
            else:
                form.save()
        else:
            print('Error: ', form.errors)
        
        self.result[self.__form_key] = form
    
    def create_and_get(self, *args, **kwargs):
        return self.post(self, get_object=True, *args, **kwargs)

    def check_valid(self, *args, **kwargs):
        form = kwargs['form'](data=kwargs['initial'])
        if form.is_valid():
            return form
        else:
            return {'error': form}

    @classonlymethod
    def get_form(self, *args, **kwargs):
        print('Self ', self)
        print('Аргументы метода вызова формы: ', args)
        self.request = args[0]

        if 'response' in kwargs:
            if kwargs['response'] == 'form':
                return self.form


"""
========================Product========================
"""


class ProductListView(GeneralListView):

    model = Product
    name = 'products'

class ProductFormView(GeneralFormView):

    form = ProductForm
    name = 'product_form'

    def response(self, *args, **kwargs):
        return self.result


"""
========================ServiceInput========================
"""

class ServiceInputListView(GeneralListView):

    model = ServiceInput
    name = 'services_input'
    # template = 'detail_view.html'

class ServiceInputFormView(GeneralFormView):

    form = ServiceInputForm
    name = 'service_input_form'

    def response(self, *args, **kwargs):
        return self.result


"""
========================ServiceOutput========================
"""



class ServiceOutputListView(GeneralListView):

    model = ServiceOutput
    name = 'services_input'
    # template = 'detail_view.html'

class ServiceOutputFormView(GeneralFormView):

    form = ServiceOutputForm
    name = 'service_input_form'

    def response(self, *args, **kwargs):
        return self.result


"""
========================Document input========================
"""


class DocumentInputListView(GeneralListView):
    
    model = DocumentInput
    template = 'index.html'
    name = 'documents'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result['document_type'] = 'input'

class DocumentInputFormView(GeneralFormView):

    model = DocumentInput
    form = DocumentInputForm
    name = 'document_form'

    def response(self, *args, **kwargs):
        return self.result

class DocumentInputDetailView(GeneralView):

    template = 'detail_view.html'

    def response(self, *args, **kwargs):
        
        document = DocumentInput.objects.get(pk=kwargs['pk'])
        products = ProductListView.filter_query(filter={'document_product_input_id': kwargs['pk']})
        services_input = ServiceInputListView.filter_query(filter={'document_service_input_id': kwargs['pk']})
        
        self.result = {
            'document': document,
            'products': products,
            'services_input': services_input,
            'document_type': 'input'}

        return super().response()

class DocumentInputProductFormView(GeneralView):

    template = 'document_create_view_product.html'

    def response(self, *args, **kwargs):

        document_form = DocumentInputForm()
        product_form = ProductForm()
        service_input_form = ServiceInputForm()

        self.result = {
            'document_form': document_form, 
            'product_form': product_form,
            'service_input_form': service_input_form,
            'document': 'input'}
        
        return super().response()


"""
========================Document output========================
"""


class DocumentOutputListView(GeneralListView):
    
    model = DocumentOutput
    template = 'index.html'
    name = 'documents'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result['document_type'] = 'output'

class DocumentOutputDetailView(GeneralView):

    template = 'detail_view.html'

    def response(self, *args, **kwargs):

        document = DocumentOutput.objects.get(pk=kwargs['pk'])
        products = ProductListView.filter_query(filter={'document_product_output_id': kwargs['pk']})
        services_output = ServiceOutputListView.filter_query(filter={'document_service_output_id': kwargs['pk']})
        self.result = {
            'document': document, 
            'products': products, 
            'services_output': services_output,
            'document_type': 'output'}
        return super().response()

class DocumentOutputFormView(GeneralFormView):

    model = DocumentOutput
    form = DocumentOutputForm
    name = 'document_form'

    def response(self, *args, **kwargs):
        return self.result
    
class DocumentOutputProductFormView(GeneralView):

    template = 'document_create_view_product.html'

    def response(self, *args, **kwargs):

        document_form = DocumentOutputForm()
        product_form = ProductForm()
        service_output_form = ServiceOutputForm()

        self.result = {
            'document_form': document_form, 
            'product_form': product_form,
            'service_output_form': service_output_form, 
            'document': 'output'}
        return super().response()



"""=========================================================================================="""


class GeneralFormViewClassy:

    # Метод post с использованием sql запросов
    @classonlymethod
    def post(self, *args, **kwargs):
        if 'form' in kwargs and 'data' in kwargs:
            obj = ModelsSQLTables.sql_post(form=kwargs['form'], fields=kwargs['data'])
            if 'get_object' in kwargs:
                if kwargs['get_object']:
                    return obj
        else:
            raise TypeError(f'Method post() must contain Django form and fields data in kwargs')

    # Метод post для классической ORM Django
    """
    @classonlymethod
    def post(self, *args, **kwargs):
        if 'form' in kwargs and 'data' in kwargs:
            form_instance = kwargs['form'](data=kwargs['data'])
        else:
            raise TypeError(f'Method post() must contain Django form and fields data in kwargs')
        
        if 'get_object' in kwargs:
            if kwargs['get_object']:
                new_object = form_instance.save()
                return new_object
        else:
            form_instance.save()
    """

    @classonlymethod
    def create_and_get(self, *args, **kwargs):
        return self.post(self, get_object=True, *args, **kwargs)

    @classonlymethod
    def check_valid(self, *args, **kwargs):
        if 'form' in kwargs and 'data' in kwargs:
            form = kwargs['form'](data=kwargs['data'])
            if form.is_valid():
                return form
            else:
                return {'errors': form}
        else:
            raise KeyError(f'check_valid() must contain form= and data= in parameters')

    # @classonlymethod
    # def get_form(self, *args, **kwargs):
    #     print('Self ', self)
    #     print('Аргументы метода вызова формы: ', args)
    #     self.request = args[0]

    #     if 'response' in kwargs:
    #         if kwargs['response'] == 'form':
    #             return self.form
            
class MultiForms(GeneralView):

    forms = {}  # В forms заносяться объекты типа Form
    foreign_object = None # объект, который должен быть возвращён
    related_object = {} # объекты которые имеют связь foreign key

    """
    realated_object задаётся принципом 
    
    {'имя_модели_отправляемое_с_запросом': 'имя_поля_foreign_key',
    ... ,}

    может поддерживать несколько моделей, связанных с foreign_object
    """
    template = None
    additional_result_data = None
    html_response_class = None

    def __init__(self, *args, **kwargs):
        self.forms_error = False
        super().__init__(*args, **kwargs)

    def get_request_data(self, *args, **kwargs):

        if self.request.method == 'POST':

            for req in self.request.POST:
                req = json.loads(req)
            
            for form, fields in req.items():
                if '_ind_form_' in form:   # Если условие верно, значит это модель множественного типа
                    form = form[:form.find('_ind_form_')]
                    mutli_form = True
                else:
                    mutli_form = False

                if form in self.forms:

                    additional_errors = self.additional_errors(form, fields)

                    if additional_errors != None:
                        form_obj = additional_errors
                    else:
                        form_obj = self.forms[form]
                        form_obj = GeneralFormViewClassy.check_valid(form=form_obj, data=fields)
                    if 'errors' in form_obj:
                        if not mutli_form:
                            self.result[form] = form_obj['errors']
                        else:
                            if form in self.result: # Проверка на наличи в result значения мультформы
                                if isinstance(self.result[form], list): # Проверка на то является сущесвтущее значение списком
                                    self.result[form].append(form_obj['errors'])
                                # Если нет, то создаётся новое значение с первой ПУСТОЙ! формой, а дальше добавляется текущее значение
                                else:
                                    self.result[form] = [self.forms[form]()]
                                    self.result[form].append(form_obj['errors'])
                            # Если значения нет, то создаётся новое значение с первой ПУСТОЙ! формой. Это важно для копирования формы в фронтенде
                            else:
                                self.result[form] = [self.forms[form]()]
                                self.result[form].append(form_obj['errors'])
                        print('==========ОШИБКИ==========', form_obj)
                        self.forms_error = True
                    else:
                        if not mutli_form:
                            self.result[form] = form_obj
                        else:
                            if form in self.result: # Проверка на наличи в result значения мультформы
                                if isinstance(self.result[form], list): # Проверка на то является сущесвтущее значение списком
                                    self.result[form].append(form_obj)
                                # Если нет, то создаётся новое значение с первой ПУСТОЙ! формой, а дальше добавляется текущее значение
                                else:
                                    self.result[form] = [self.forms[form]()]
                                    self.result[form].append(form_obj)
                            # Если значения нет, то создаётся новое значение с первой ПУСТОЙ! формой. Это важно для копирования формы в фронтенде
                            else:
                                self.result[form] = [self.forms[form]()]
                                self.result[form].append(form_obj)
                    
                    if self.additional_result_data != None:
                        try: 
                            self.result.update(self.additional_result_data)
                        except:
                            raise TypeError(f'"additional_result_data" must contain dict, but get {self.additional_result_data}')
                else:
                    raise KeyError(f"Форма {form} не обнаружена, либо не была указана")
            
            if not self.forms_error:
                self.multi_form_post(request=req)
                # Логика, которая должна релизовываться, если ошибок в формах нет

    def multi_form_post(self, *args, **kwargs):

        if 'request' in kwargs:
            for form, fields in kwargs['request'].items():
                if '_ind_form_' in form:   # Если условие верно, значит это модель множественного типа
                    form = form[:form.find('_ind_form_')]
                    mutli_form = True
                else:
                    mutli_form = False

                if form in self.forms:

                    additional_action = self.additional_actions_for_post(form, fields)

                    if additional_action != None:
                    
                        if 'fields' in additional_action:
                            fields = additional_action['fields']
                        if 'form' in additional_action:
                            form = additional_action['form']

                    form_obj = self.forms[form]

                    if not mutli_form:
                        self.foreign_object = GeneralFormViewClassy.create_and_get(form=form_obj, data=fields)
                    else:
                        fields[self.related_object[form]] = self.foreign_object.id
                        GeneralFormViewClassy.post(form=form_obj, data=fields)
                else:
                    raise KeyError(f"Форма {form} не обнаружена, либо не была указана")
    
    def additional_errors(self, form, fields, *args, **kwargs):
        # Этот метод будет использоваться если в дочернем классе в форму и поля нужно будет
        # добавить дополнительные ошибки для вывода
        return None

    def additional_actions_for_post(self, form, fields, *args, **kwargs):
        # Этот метод будет использоваться если в дочернем классе c формой и полями нужно будет провести
        # дополнительные действия перед сохранением в базу данных
        pass

    def response(self, *args, **kwargs):
        if self.forms_error:
            print('Есть ошибки в формах: ', self.forms_error)
            return super().response()
        else:
            print('Ответ идёт заданым методом')
            print('Foreing объект: ', self.foreign_object)
            return self.html_response_class.as_view(self.request, pk=self.foreign_object.pk)
        
    @classonlymethod
    def as_view(cls, *args, **kwargs):
        self = cls(*args, **kwargs)
        self.get_request_data(*args, **kwargs)
        return self.response()
    

class DocumentInputMultiForms(MultiForms):

    forms = {'document_form': DocumentInputForm,
            'product_form': ProductForm,
            'service_input_form': ServiceInputForm}

    foreign_object = 'document_form'
    related_object = {
        'product_form': 'document_product_input',
        'service_input_form': 'document_service_input'}

    template = 'document_create_view_product.html'

    additional_result_data = {'document': 'input'}
    html_response_class = DocumentInputDetailView

    def additional_actions_for_post(self, form, fields, *args, **kwargs):
        if form == 'product_form' and 'quantity' in fields:
            fields['balance'] = fields['quantity']
            return {'fields': fields}
    
class DocumentOutputMultiForms(MultiForms):

    forms = {'document_form': DocumentOutputForm,
            'product_form': ProductForm,
            'service_output_form': ServiceOutputForm}

    foreign_object = 'document_form'
    related_object = {
        'product_form': 'document_product_output',
        'service_output_form': 'document_service_output'}
    
    template = 'document_create_view_product.html'

    additional_result_data = {'document': 'output'}
    html_response_class = DocumentOutputDetailView

    def __init__(self, *args, **kwargs):
        self.product_balance_parameters = []
        super().__init__(*args, **kwargs)

    def additional_errors(self, form, fields, *args, **kwargs):

        if form == 'product_form' and 'quantity' in fields:
            print('Запуск обработки количества товара в остатке и запросе')
            if isinstance(fields['quantity'], str) and fields['quantity'] != '':
                quantity = Decimal(fields['quantity'])
            else:
                return None

            queryset = Product.objects.filter(Q(product_index=fields['product_index']) & ~Q(balance=0)).order_by('document_product_input__date')
            total_balance = queryset.aggregate(sum_balance=Sum('balance'))
            
            if quantity > total_balance['sum_balance']:
                print('Товара не хватает на складе')
                form_obj = self.forms[form]
                form_obj = GeneralFormViewClassy.check_valid(form=form_obj, data=fields)
                form_obj['errors'].add_error('quantity', 'Не хватает товара на складе')

                return form_obj
            else:
                self.product_balance_parameters.append({
                    'queryset': queryset,
                    'quantity': quantity
                    })
                print('В обработку остатка и запросов товара будут добавлені следующие элементы: ', self.product_balance_parameters)
                return None

    def set_product_balance(self, *args, **kwargs):
        if self.product_balance_parameters != []:
            print('Параметры для обработки остатка товара: ', self.product_balance_parameters)
            for parameters in self.product_balance_parameters:

                quantity = parameters['quantity']

                for obj in parameters['queryset']:
                    print('Запрос: ', quantity, ' остаток товара: ', obj.balance)
                    if obj.balance == None:
                        continue
                    print('Результат сравнения: ', quantity <= obj.balance)
                    if quantity <= obj.balance:
                        print('Товара хватает, остаток в позиции: ', obj.balance - quantity)
                        obj.balance = obj.balance - quantity
                        obj.save()
                        break
                    else:
                        print('Товара не хватает, в следующую позицию будет передано: ', quantity - obj.balance)
                        quantity = quantity - obj.balance
                        obj.balance = 0
                        obj.save()

    def multi_form_post(self, *args, **kwargs):
        self.set_product_balance()
        return super().multi_form_post(*args, **kwargs)
    
class ProductBalanceView(GeneralView):

    template = 'products_balance.html'

    def __init__(self, *args, **kwargs):
        self.product_indexes = {}
        self.products_balance = {}
        self.storage = []
        super().__init__(*args, **kwargs)
    
    def response(self, *args, **kwargs):
        products = Product.objects.filter(~Q(document_product_input = None) & ~Q(balance=0))
        print('Остаток товара: ', products)
        for product in products:

            storage = product.document_product_input.storage

            if storage.storage not in self.product_indexes:
                self.product_indexes[storage.storage] = []
            
            if product.product_index not in self.product_indexes[storage.storage]:
                
                print('имеющийся список: ', self.product_indexes)
                print('Склад: ', product.document_product_input.storage)
                self.product_indexes[storage.storage].append(product.product_index)
                
                products_by_index = Product.objects.filter(product_index=product.product_index, document_product_input__storage=storage)
                products_sum_price = products_by_index.aggregate(sum=Sum('price'))
                products_sum_quantity = products_by_index.aggregate(sum=Sum('balance'))

                products_balance_storage = {
                    'name': product.nomenclature,
                    'quantity': products_sum_quantity['sum'],
                    'price': products_sum_price['sum'],
                    'index': product.product_index
                    }

                if storage.storage not in self.products_balance:
                    self.products_balance[storage.storage] = [products_balance_storage]
                else:
                    self.products_balance[storage.storage].append(products_balance_storage)

        self.result['products_balance'] = self.products_balance

        return super().response(*args, **kwargs)