from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.http import QueryDict

from django.db.models import Q
from django.db.models import Sum

from django.utils.decorators import classonlymethod
import json
import ast

from .forms import *
from .models import *

from django.apps import apps

from django.middleware.csrf import get_token
# Create your views here.

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
    def filter_query(self, *args, **kwargs): # возможность будущей реализации фильра данных
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

# class MultiForms(GeneralView):

#     forms = {}  # В forms заносяться объекты типа GeneralFormView
#     foreign_object = None # объект, который должен быть возвращён
#     related_object = {} # объекты которые имеют связь foreign key

#     """
#     realated_object задаётся принципом 
    
#     {'имя_модели_отправляемое_с_запросом': 'имя_поля_foreign_key',
#     ... ,}

#     может поддерживать несколько моделей, связанных с foreign_object
#     """

#     forms_error = False

#     # @classonlymethod
#     def request_data(self, *args, **kwargs):

#         # self.request = request

#         print('Хранилище foreign_object: ', self.foreign_object)

#         if self.request.method == 'POST':

#             for req in self.request.POST:
#                 req = json.loads(req)
#                 print('Это self.request: ', req)
#             for model, fields in req.items():
#                 if '_ind_form_' in model:
#                     model = model[:model.find('_ind_form_')]
#                     print('Модель n-го типа')
#                     print('Модель одиночного типа')
#                 else:
#                     print('Модель одиночного типа')
#                     print(f"{model}: {fields}")
#                 if model in self.forms:
                    
#                     form_view = self.forms[model]()
#                     form_view.check_valid(form_view, form=form_view.form, initial=fields)
#                     if not self.forms_error:
#                         self.multi_form_post(form_view=form_view, model=model, fields=fields)
#                     # print('Просмотр формы: ', form_view)
#                     # print('Форма в просмотре формы: ', form_view.form)
#                     # print('Модель foreign типа: ', model == self.foreign_object)
#                     # print('Это объект related: ', self.related_object)
#                     """"""
#                     # if model == self.foreign_object:    # Проверка на то, является ли модель foreign для другой модели
#                     #     self.foreign_object = form_view.create_and_get(form_view, form=form_view.form, initial=fields)
#                     #     print('Записан FOREIGN OBJECT: ', self.foreign_object)
#                     # elif model in self.related_object:  # Проверка на то, есть ли у модели foreign связь с другой моделью
#                     #     print('Используется FOREIGN OBJECT: ', self.foreign_object)
#                     #     fields[self.related_object[model]] = self.foreign_object
#                     #     print('Связанное поле: ', self.related_object[model])
#                     #     form_view.post(form_view, form=form_view.form, initial=fields)
#                     # else:
#                     #     form_view.post(form_view, form=form_view.form, initial=fields)
#                     #     print('Обнаружена форма: ', form_view)
#                     #     for key, value in fields.items():
#                     #         print(f"{key}: {value}")
#                 else:
#                     raise KeyError(f"Форма {model} не обнаружена, либо не была указана")

#     def form_validation_check(self, *args, **kwargs):
#         form_view = self.forms[kwargs['model']]
#         form_check = form_view.check_valid(form_view, form=form_view.form, initial=kwargs['fields'])
#         # print(form_check['error'])
#         if 'error' in form_check:
#             if kwargs['model'] == kwargs['multi_form']:
#                 print('результат мульти модель')
#                 if kwargs['model'] in self.result:
#                     if isinstance(self.result[kwargs['model']], list):
#                         print('СПИСОК УЖЕ ЕСТЬ')
#                         self.result[kwargs['model']].append(form_check['error'])
#                         print('ЭТО ВНЕСЛИ В СУЩЕСТВУЮЩИЙ СПИСОК: ', self.result[kwargs['model']])
#                         print(self.result)
#                 else:
#                     print('СПИСКА ЕЩЁ НЕТ')
#                     self.result[kwargs['model']] = [form_check['error'].__class__()]
#                     self.result[kwargs['model']].append(form_check['error'])
#                     print('ЭТО ВНЕСЛИ В НЕ СУЩЕСТВУЮЩИЙ СПИСОК: ', self.result[kwargs['model']])
#                     print(self.result)
#             elif kwargs['multi_form'] == None:
#                 print('результат НЕ мульти модель')
#                 self.result[kwargs['model']] = form_check['error']
#             self.forms_error = True
#         else:
#             if kwargs['model'] == kwargs['multi_form']:
#                 if kwargs['model'] in self.result:
#                     if isinstance(self.result[kwargs['model']], list):
#                         self.result[kwargs['model']] = self.result[kwargs['model']].append(form_check)
#                 else:
#                     self.result[kwargs['model']] = [form_check.__class__()]
#                     self.result[kwargs['model']].append(form_check)
#             else:
#                 self.result[kwargs['model']] = form_check

#     def multi_form_post(self, *args, **kwargs):
#         print('============Запущен метод поста мультиформы============')
#         if kwargs['model'] == self.foreign_object:    # Проверка на то, является ли модель foreign для другой модели
#             self.foreign_object = kwargs['form_view'].create_and_get(kwargs['form_view'], form=kwargs['form_view'].form, initial=kwargs['fields'])
#             print('Записан FOREIGN OBJECT: ', self.foreign_object)
#         elif kwargs['model'] in self.related_object:  # Проверка на то, есть ли у модели foreign связь с другой моделью
#             print('Используется FOREIGN OBJECT: ', self.foreign_object)
#             kwargs['fields'][self.related_object[kwargs['model']]] = self.foreign_object
#             print('Связанное поле: ', self.related_object[kwargs['model']])
#             kwargs['form_view'].post(kwargs['form_view'], form=kwargs['form_view'].form, initial=kwargs['fields'])
#         else:
#             kwargs['form_view'].post(kwargs['form_view'], form=kwargs['form_view'].form, initial=kwargs['fields'])
#             print('Обнаружена форма: ', kwargs['form_view'])
#             for key, value in kwargs['fields'].items():
#                 print(f"{key}: {value}")

        
#     @classonlymethod
#     def as_view(cls, *args, **kwargs):
#         self = cls(*args, **kwargs)
#         self.request_data(*args, **kwargs)
#         return self.response()


"""
========================Product========================
"""


class ProductListView(GeneralListView):

    model = Product
    name = 'products'
    # template = 'detail_view.html'

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
            'services_input': services_input}

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

# class DocumentInputMultiForms(MultiForms):

#     foreign_object = 'document_form'
#     related_object = {
#         'product_form': 'document_product_input',
#         'service_input_form': 'document_service_input'}


#     forms = {'document_form': DocumentInputFormView(),
#              'product_form': ProductFormView(),
#              'service_input_form': ServiceInputFormView()}

#     template = 'document_create_view_product.html'

#     def request_data(self, *args, **kwargs):
#         # Копирование данных поля количества товара в поле остатка товара
#         for req in self.request.POST:
#             req = json.loads(req)
        
#         for model, fields in req.items():

#             if '_ind_form_' in model:
#                 model = model[:model.find('_ind_form_')]
#                 multi_form = model
#             else:
#                 multi_form = None

#             if model == 'product_form' and 'quantity' in fields:
#                 fields['balance'] = fields['quantity']

#                 query = QueryDict(json.dumps(req), mutable=True)
#                 self.request.POST = query

#             self.form_validation_check(model=model, multi_form=multi_form, fields=fields)
#             self.result['document'] = 'input'

#         if not self.forms_error:
#             super().request_data(*args, **kwargs)

#     def response(self, *args, **kwargs):
#         if not self.forms_error:
#             return DocumentInputDetailView.as_view(self.request, pk=self.foreign_object.pk)
#         else:
#             return super().response()


"""
========================Document output========================
"""


class DocumentOutputListView(GeneralListView):
    
    model = DocumentOutput
    template = 'index.html'
    name = 'documents'

class DocumentOutputDetailView(GeneralView):

    template = 'detail_view.html'

    def response(self, *args, **kwargs):

        document = DocumentOutput.objects.get(pk=kwargs['pk'])
        products = ProductListView.filter_query(filter={'document_product_input_id': kwargs['pk']})
        self.result = {'document': document, 'products': products}
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
    
# class DocumentOutputMultiForms(MultiForms):

#     foreign_object = 'document_form'
#     related_object = {
#         'product_form': 'document_product_output',
#         'service_output_form': 'document_service_output'}


#     forms = {'document_form': DocumentOutputFormView,
#              'product_form': ProductFormView,
#              'service_output_form': ServiceOutputFormView}
    
#     template = 'document_create_view_product.html'

#     def request_data(self, *args, **kwargs):
#         print('Запущена обработка данных мультиформы для создания исходящей декларации')
#         print(self.request.POST)
#         # Копирование данных поля количества товара в поле остатка товара
#         for req in self.request.POST:
#             req = json.loads(req)
        
#         for model, fields in req.items():
#             if '_ind_form_' in model:
#                 model_name = model[:model.find('_ind_form_')]
#                 multi_form = model_name
#             else:
#                 model_name = model
#                 multi_form = None

#             self.form_validation_check(model=model_name, multi_form=multi_form, fields=fields)
#             self.result['document'] = 'output'

#             if self.forms_error:
#                 continue

#             if model_name == 'product_form' and 'quantity' in fields:
#                 print('Количество товара который должен отпускаться на продажу: ', fields['quantity'])
#                 print('Индекс товара: ', fields['product_index'])
                
#                 queryset = Product.objects.filter(Q(product_index=fields['product_index']) & ~Q(balance=0)).order_by('document_product_input__date')
#                 print('Отсортированные продукты по дате деклараций: ', queryset)
#                 total_balance = queryset.aggregate(sum_balance=Sum('balance'))
#                 print('Total balance', total_balance)
#                 print('Total balane key', total_balance['sum_balance'])
#                 quantity = int(fields['quantity'])
#                 if quantity > total_balance['sum_balance']:
#                     print('Товара на складе не хватает')
#                     form = self.forms[model_name].form(data=fields)
#                     form.add_error('quantity', 'Не хватает товара на складе')
#                     if isinstance(self.result[model_name], list):
#                         print('Формы уже идёт списком')
#                         self.result[model_name].append(form)
#                     else:
#                         print('Создаю новый список')
#                         self.result[model_name] = [form]
#                     continue
#                 for obj in queryset:
#                     print('Quantity: ', quantity)
#                     result = self.get_product_balance(quantity, obj, fields)
#                     if result == 'break':
#                         break
#                     else:
#                         print('ЭТО ТО, ЧТО ВЕРНУЛА ФУНКЦИЯ: ', result)
#                         quantity = result

#                 # query = QueryDict(json.dumps(req), mutable=True)
#                 # self.request.POST = query

#         if not self.forms_error:
#             super().request_data(*args, **kwargs)

#     # def response(self, *args, **kwargs):
#     #     if 'result' in kwargs:
#     #         print('Результаты ответа сервера', kwargs['result'])
#     #         return kwargs['result']
#     #     return DocumentOutputDetailView.as_view(self.request, pk=self.foreign_object.pk)

#     def get_product_balance(self, quantity, obj, fields):
#         try:
#             print('Название: ', obj.nomenclature, ' ===Дата: ', obj.document_product_input.date, 'количество: ', obj.balance)
#             print('Запрос количества товара: ', quantity)
#             form = ProductForm(fields)
#                 # print('ФОРМА: ', form)
#             if form.is_valid():
#                 print('+++Данные формы заполнены верно+++')
#                 if quantity <= obj.balance:
#                     print('Товара хватает, остаток в позиции: ', obj.balance - quantity)
#                     # Здесь надо будет сделать пересохранение данной модели с новым балансом
#                     print('Поля формы: ', fields)
#                     obj.balance = obj.balance - quantity
#                     obj.save()
#                     return 'break'
#                 else:
#                     print('Товара не хватает, в следующую позицию будет передано: ', quantity - obj.balance)
#                     # Здесь реализовать сохранение нулевого баланса в модель продукта
#                     result = quantity - obj.balance
#                     obj.balance = 0
#                     obj.save()
#                     return result
#             else:
#                 for e, i in form.errors.items():
#                     print('Ошибка', e, i)
#                 print('---Данные формы заполнены не верно---')
#         except AttributeError:
#             print('Ошибка. Отсутвует связанный документ')
#             return quantity


"""=========================================================================================="""


class GeneralFormViewClassy:

    # form = None
    # name = None

    # __form_key = None

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.__get_request_method__(*args, **kwargs)

    # def __get_request_method__(self, *args, **kwargs):
    #     print('ЗАПУЩЕН КЛАСС ПОЛУЧЕНИЯ ФОРМЫ', self)
    #     if self.name != None:
    #         self.__form_key = self.name
    #     else:
    #         self.__form_key = self.form.__class__.__name__

    #     if self.request != None:
    #         if self.request.method == 'POST':
    #             self.post()
    #         elif self.request.method == 'GET':
    #             if 'pk' in kwargs:
    #                 self.__object = self.form._meta.model.objects.get(id=kwargs['pk'])
    #                 self.__get_update_form__()
    #             else:
    #                 self.__get__()

    # def __get__(self, *args, **kwargs):
    #     self.result[self.__form_key] = self.form()

    # def __get_update_form__(self, *args, **kwargs):
    #     self.result[self.__form_key] = self.form(instance=self.__object)
    
    @classonlymethod
    def post(self, *args, **kwargs):
        print('Аргументы в kwargs .post(): ', kwargs)
        print('Форма: ', kwargs['form'])
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

    @classonlymethod
    def create_and_get(self, *args, **kwargs):
        print('Аргументы в kwargs .create_and_get(): ', kwargs)
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
    forms_error = False
    html_response_class = None

    def get_request_data(self, *args, **kwargs):

        if self.request.method == 'POST':

            for req in self.request.POST:
                req = json.loads(req)
                # print('Это self.request: ', req)
            
            for form, fields in req.items():
                if '_ind_form_' in form:   # Если условие верно, значит это модель множественного типа
                    form = form[:form.find('_ind_form_')]
                    mutli_form = True
                else:
                    mutli_form = False

                if form in self.forms:
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
                pass
                self.multi_form_post(request=req)
                # Логика, которая должна релизовываться, если ошибок в формах нет
            else:
                pass
                # Реализовать возврат всех заполненных форм с ошибками
                # Если есть ошибки, они уже были записаны в self.result и метод response должен всё вернуть

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
                    print('Дополнительные действия: ', additional_action)
                    if additional_action != None:
                    
                        if 'fields' in additional_action:
                            fields = additional_action['fields']
                        if 'form' in additional_action:
                            form = additional_action['form']

                    form_obj = self.forms[form]

                    if not mutli_form:
                        self.foreign_object = GeneralFormViewClassy.create_and_get(form=form_obj, data=fields)
                        print('FOREIGN KEY========================', self.foreign_object)
                    else:
                        fields[self.related_object[form]] = self.foreign_object.id
                        GeneralFormViewClassy.post(form=form_obj, data=fields)
                else:
                    raise KeyError(f"Форма {form} не обнаружена, либо не была указана")
            
    def additional_actions_for_post(self, form, fields, *args, **kwargs):
        # Этот метод будет использоваться если в дочернем классе в формой и полями нужно будет провести
        # дополнительные действия перед сохранением в базу данных
        pass

    def response(self, *args, **kwargs):
        if self.forms_error:
            return super().response()
        else:
            print('Ответ идёт заданым методом')
            print('Foreing объект: ', self.foreign_object)
            return self.html_response_class.as_view(self.request, pk=self.foreign_object.pk)

    # def form_validation_check(self, *args, **kwargs):
    #     form_view = self.forms[kwargs['model']]
    #     form_check = form_view.check_valid(form_view, form=form_view.form, initial=kwargs['fields'])
    #     # print(form_check['error'])
    #     if 'error' in form_check:
    #         if kwargs['model'] == kwargs['multi_form']:
    #             print('результат мульти модель')
    #             if kwargs['model'] in self.result:
    #                 if isinstance(self.result[kwargs['model']], list):
    #                     print('СПИСОК УЖЕ ЕСТЬ')
    #                     self.result[kwargs['model']].append(form_check['error'])
    #                     print('ЭТО ВНЕСЛИ В СУЩЕСТВУЮЩИЙ СПИСОК: ', self.result[kwargs['model']])
    #                     print(self.result)
    #             else:
    #                 print('СПИСКА ЕЩЁ НЕТ')
    #                 self.result[kwargs['model']] = [form_check['error'].__class__()]
    #                 self.result[kwargs['model']].append(form_check['error'])
    #                 print('ЭТО ВНЕСЛИ В НЕ СУЩЕСТВУЮЩИЙ СПИСОК: ', self.result[kwargs['model']])
    #                 print(self.result)
    #         elif kwargs['multi_form'] == None:
    #             print('результат НЕ мульти модель')
    #             self.result[kwargs['model']] = form_check['error']
    #         self.forms_error = True
    #     else:
    #         if kwargs['model'] == kwargs['multi_form']:
    #             if kwargs['model'] in self.result:
    #                 if isinstance(self.result[kwargs['model']], list):
    #                     self.result[kwargs['model']] = self.result[kwargs['model']].append(form_check)
    #             else:
    #                 self.result[kwargs['model']] = [form_check.__class__()]
    #                 self.result[kwargs['model']].append(form_check)
    #         else:
    #             self.result[kwargs['model']] = form_check

    # def multi_form_post(self, *args, **kwargs):
    #     print('============Запущен метод поста мультиформы============')
    #     if kwargs['model'] == self.foreign_object:    # Проверка на то, является ли модель foreign для другой модели
    #         self.foreign_object = kwargs['form_view'].create_and_get(kwargs['form_view'], form=kwargs['form_view'].form, initial=kwargs['fields'])
    #         print('Записан FOREIGN OBJECT: ', self.foreign_object)
    #     elif kwargs['model'] in self.related_object:  # Проверка на то, есть ли у модели foreign связь с другой моделью
    #         print('Используется FOREIGN OBJECT: ', self.foreign_object)
    #         kwargs['fields'][self.related_object[kwargs['model']]] = self.foreign_object
    #         print('Связанное поле: ', self.related_object[kwargs['model']])
    #         kwargs['form_view'].post(kwargs['form_view'], form=kwargs['form_view'].form, initial=kwargs['fields'])
    #     else:
    #         kwargs['form_view'].post(kwargs['form_view'], form=kwargs['form_view'].form, initial=kwargs['fields'])
    #         print('Обнаружена форма: ', kwargs['form_view'])
    #         for key, value in kwargs['fields'].items():
    #             print(f"{key}: {value}")

        
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
        print('Запущен метод дополнительных действий в дочернем методе')
        print('Form: ', form)
        print('Fields: ', fields)
        if form == 'product_form' and 'quantity' in fields:
            fields['balance'] = fields['quantity']
            return {'fields': fields}