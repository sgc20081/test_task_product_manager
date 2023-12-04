$(function(){
    function skript_activation(){
        // alert('Скрипт включен')

        // Перехват события по ссылке
        new EventInterception(properties={
            element: document.getElementsByTagName('a'),
            success: function(response){
                console.log('Ответ от сервера: ', response.data)
                let temp_elem = $('<div>').html(response.data);
                let content = temp_elem.find('.main_container').html();

                $('.main_container').html(content);
                skript_activation()
            }
        })

        // Перехват события по форме
        new EventInterception(properties={
            element: document.getElementsByTagName('form'),
            success: function(response){
                console.log('Ответ от сервера: ', response.data)
                let temp_elem = $('<div>').html(response.data);
                let content = temp_elem.find('.main_container').html();

                $('.main_container').html(content);
                skript_activation()
            }
        })

        // Создание нескольких копий форм ПОД ТОВАРЫ, на основе формы ДЛЯ ТОВАРОВ, приходящей с сервера 
        new MultipleForm({
            form: document.getElementById('product'), 
            add_form_btn: document.querySelector('.add_product_button'),
            del_form_btn_selector: '.delete_form',
            columns_selector: '.product_columns_name',
            parent_container: document.querySelector('.product_forms_container')
        })

        // Создание нескольких копий форм ПОД ПОСТУПАЮЩИЕ УСЛУГИ, на основе формы ДЛЯ ПОСТУПАЮЩИХ УСЛУГ, приходящей с сервера
        new MultipleForm({
            form: document.getElementById('service_input'),
            add_form_btn: document.querySelector('.add_service_input_button'),
            del_form_btn_selector: '.delete_form',
            columns_selector: '.service_input_columns_name',
            parent_container: document.querySelector('.service_input_forms_container')
        })

        // Создание нескольких копий форм ПОД ИСХОДЯЩИЕ УСЛУГИ, на основе формы ДЛЯ ИСХОДЯЩИХ УСЛУГ, приходящей с сервера
        new MultipleForm({
            form: document.getElementById('service_output'),
            add_form_btn: document.querySelector('.add_service_output_button'),
            del_form_btn_selector: '.delete_form',
            columns_selector: '.service_output_columns_name',
            parent_container: document.querySelector('.service_output_forms_container')
        })

        // Вывод суммы для форм продуктов
        new PriceSum({
            forms_selector: '.multi_form_product',
            quantity_selector: '[name="quantity"]',
            price_selector: '[name="price"]',
            sum_price_selector: '[name="sum_price"]',
            tax_rate_selector: '[name="tax_rate"]',
            sum_tax_rate_selector: '[name="tax_rate_sum_price"]',
            all_sum: document.querySelector('.all_sum_price'),
            add_form_btn: document.querySelector('.add_form_product'),
        })

        // Вывод суммы для форм исходящих услуг
        new PriceSum({
            forms_selector: '.multi_form_service_input',
            quantity_selector: '[name="quantity"]',
            price_selector: '[name="price"]',
            sum_price_selector: '[name="sum_price"]',
            tax_rate_selector: '[name="tax_rate"]',
            sum_tax_rate_selector: '[name="tax_rate_sum_price"]',
            all_sum: document.querySelector('.all_sum_price'),
            add_form_btn: document.querySelector('.add_form_service'),
        })

        // Вывод суммы для форм входящих услуг
        new PriceSum({
            forms_selector: '.multi_form_service_output',
            quantity_selector: '[name="quantity"]',
            price_selector: '[name="price"]',
            sum_price_selector: '[name="sum_price"]',
            // tax_rate_selector: '[name="tax_rate"]',
            // sum_tax_rate_selector: '[name="tax_rate_sum_price"]',
            all_sum: document.querySelector('.all_sum_price'),
            add_form_btn: document.querySelector('.add_form_service'),
        })
        
        if ($('#document').attr('document') == 'input'){
            // Класс, отвечающий за отправку нескольких форм в запросе при создании входящей 
            // накладной ДЛЯ ТОВАРОВ И УСЛУГ
            console.log('Создаётся мултиформа для отправки входящей накладной')
            let document_input_multiform = new MultipleFormSend({
                forms: {
                    'document_form': document.getElementById('document_input_form'),
                    'product_form': document.getElementsByClassName('multi_form_product'),
                    'service_input_form': document.getElementsByClassName('multi_form_service_input')
                },
                forms_send_btn: document.querySelector('.document_input_send_forms_btn'),
                url: 'multi-form-document-input',
                success(response){
                    let self = document_input_multiform;

                    console.log('Ответ от сервера: ', response.data)
                    let temp_elem = $('<div>').html(response.data);
                    let content = temp_elem.find('.main_container').html();

                    $('.main_container').html(content);
                    
                    self.forms_id_order(self.forms.product_form[0]);
                    self.forms_id_order(self.forms.service_input_form[0]);

                    skript_activation();
                }
            })
            }
            
            else if ($('#document').attr('document') == 'output'){
            // Класс, отвечающий за отправку нескольких форм в запросе при создании исходящей 
            // накладной ДЛЯ ТОВАРОВ И УСЛУГ
            console.log('Создаётся мултиформа для отправки исходящей накладной')
            let document_ouput_multiform = new MultipleFormSend({
                forms: {
                    'document_form': document.getElementById('document_output_form'),
                    'product_form': document.getElementsByClassName('multi_form_product'),
                    'service_output_form': document.getElementsByClassName('multi_form_service_output')
                },
                forms_send_btn: document.querySelector('.document_output_send_forms_btn'),
                url: 'multi-form-document-output',
                success(response){
                    let self = document_ouput_multiform;

                    console.log('Ответ от сервера: ', response.data)
                    let temp_elem = $('<div>').html(response.data);
                    let content = temp_elem.find('.main_container').html();

                    $('.main_container').html(content);
                    
                    self.forms_id_order(self.forms.product_form[0]);
                    self.forms_id_order(self.forms.service_output_form[0]);

                    skript_activation()
                }
            })
        }
    }
    skript_activation()
})

class EventInterception {
    constructor(properties){

        this.element = properties.element;

        this.url = null;
        this.type = null;
        this.data = null;
        this.headers = null;

        if (typeof(properties.success) === 'function') {
            this.success = properties.success;
        } else if(properties.success === undefined) {
            throw new Error('EventInterception. You must use the \'success\' method, when instantiating the class, to interact with the response from the server')
        } else {
            throw new Error('EventInterception. You must specify the function to be executed after receiving the response from the server. \n\n\'success\' method')
        }

        this.event_stop();
    }

    event_stop() {
        let self = this;

        $.each(this.element, function(ind, elem){
            if (elem.tagName.toLowerCase() == 'a'){
                $(elem).click(function(event){
                    event.preventDefault();

                    self.url = elem.href;
                    console.log('Url: ', elem.href);
                    console.log('Зафиксирована попытка перехода');
                    self.type = 'GET';

                    self.send_ajax();
                })
            }
            else if (elem.tagName.toLowerCase() == 'form'){
                console.log('Зафиксирована форма')
                $(elem).submit(function(event){
                    console.log('Попытка отпрвки формы')
                    event.preventDefault();
                    console.log('Location: ', elem.location)
                    console.log('Action: ', elem.action)
                    console.log('Self.url: ', window.location.url)
                    if (elem.location !== undefined){
                        self.url = elem.location;
                    }
                    else if (elem.action !== undefined){
                        self.url = elem.action;
                    }
                    else {
                        self.url = window.location.href;
                    }
                    console.log('Loacation of form: ', elem.location, elem.action)
                    self.type = 'POST';
                    self.data = {};

                    let form_data = $(elem).serializeArray();

                    form_data.forEach(function(item){
                        if (item.name == 'csrfmiddlewaretoken'){
                            self.headers = {'X-CSRF-TOKEN': item.value}
                        }
                        console.log(`Field: ${item.name}, value: ${item.value}`)
                        self.data[item.name] = item.value
                    })
                    console.log('Url формы для отправки: ', self.url)
                    console.log('Метод формы для отправки: ', self.type)
                    console.log('Заголовки формы для отправки: ', self.headers)
                    console.log('Данные формы для отправки: ', self.data)
                    self.send_ajax()
                })
            }
        })
    }

    send_ajax() {
        console.log('отправляю ajax запрос')
        let self = this;
        $.ajax({
            url: self.url,
            type: self.type,
            data: self.data,
            headers: self.headers,
            dataType: 'json',
            success: function(response){
                //window.location.href = self.url
                self.success(response)
            },
        })
    }

}

class MultipleForm{
    constructor(properties){
        this.form = $(properties.form);
        this.add_form_btn = $(properties.add_form_btn);
        this.del_form_btn_selector = properties.del_form_btn_selector;
        this.columns_selector = properties.columns_selector;
        this.parent_container = $(properties.parent_container);

        this.cloned_form_id = 1;

        this.add_form_btn.on('click', this.copy_form.bind(this))
        console.log('Кнопка добавления формы: ', this.add_form_btn)
    }

    add_form_btn_event(){

    }

    copy_form(){
        let self = this
        let form_id = this.form.attr('id')
        let cloned_form = this.form.clone()

        if (this.parent_container.find('form').length > 1 && this.cloned_form_id == 1){
            console.log('Форм больше одной')
            console.log(this.parent_container.find('form'))
            let forms = this.parent_container.find('form')
            let last_form = forms[forms.length - 1]
            console.log(last_form)
            let last_form_id = $(last_form).attr('id').slice($(last_form).attr('id').lastIndexOf('_')+1)
            this.cloned_form_id = parseInt(last_form_id)+1
            console.log(this.cloned_form_id)
        }

        cloned_form.attr('id', form_id + '_' + this.cloned_form_id.toString())
        cloned_form.find(this.del_form_btn_selector).on('click', this.delete_form.bind(this, cloned_form))

        this.cloned_form_id++
        console.log(this.cloned_form_id)
        
        if(this.cloned_form_id >= 1){
            $(this.columns_selector).show()
        }

        this.parent_container.append(cloned_form.show())
    }

    delete_form(cloned_form){
        cloned_form.remove()
        this.cloned_form_id--

        if(this.cloned_form_id <= 1){
            $(this.columns_selector).hide()
        }
        
    }
}

class MultipleFormSend {
    constructor(properties) {

        this.forms = properties.forms;
        this.forms_send_btn = $(properties.forms_send_btn);

        this.url = properties.url;
        this.headers = {};

        this.success = properties.success;

        this.forms_send_btn.on('click', this.get_forms.bind(this));
    }

    html_collection_check(obj){
        return obj instanceof HTMLCollection
    }

    get_forms(){
        let self = this
        let form_data = {}

        function unpacking_html_collection(forms) {
            console.log('Распковка данных  форм: ', forms)
            $.each(forms, function(key, form){
                if (!self.html_collection_check(form)){

                    console.log(self,': Начинаю обработку формы')

                    let data = {};
                    console.log(form);

                    $.each($(form).find('input'), function(ind, field){
                        if (field.disabled){
                            field.disabled = false;
                        }
                    })
                    
                    new FormData(form).forEach(function(value, key){
                        console.log('Key ', key)
                        console.log('Val ', value)
                        if (key == 'csrfmiddlewaretoken') {
                            self.headers = value;
                            return true
                        }
                        data[key] = value
                    })
                    form_data[key] = data
                    console.log('Данные формы: ', form_data)
                }
                else {
                    console.log('Обнаружен набор форм: ', form)
                    let form_dict = {}
                    $.each(form, function(ind, val){
                        console.log(`Распаковка набора форм: key: ${ind}, value ${val}`)
                        if(ind != 0){
                            form_dict[key+`_ind_form_${ind}`] = val
                        }
                    })
                    console.log('Пакет форм: ', form_dict)
                    unpacking_html_collection(form_dict)
                }
            })
        }
        unpacking_html_collection(this.forms)
        console.log('Сенд аякс: ', form_data)
        this.send_ajax(form_data)
    }

    send_ajax(data){
        let self = this;
        console.log('Отправляемые данные: ', JSON.stringify(data))
        console.log(self.headers) 
        $.ajax({
            url: self.url,
            type: 'post',
            data: JSON.stringify(data),
            beforeSend: function(xhr, settings) {
                // Получаем значение CSRF-токена из куки (если используется cookiecutter Django)
                // Добавляем CSRF-токен к заголовкам запроса
                xhr.setRequestHeader("X-CSRFToken", self.headers);
            },
            // headers: {
            //     'X-CSRF-TOKEN': self.headers},
            dataType: 'json',
            success: function(response){
                //window.location.href = self.url
                self.success(response)
            },
        })
    }

    forms_id_order(form){
        console.log('Операции с:', form)
        if ($(`form#${$(form).attr('id')}`).length > 1){
            console.log('Атрибут ', $(`form#${$(form).attr('id')}`))
            let i = 1;
            console.log('Форм больше одной')
            $.each($(`form#${$(form).attr('id')}`), function(ind, form){
                if (ind != 0){
                    $(form).attr('id', `${$(form).attr('id')}_${i}`);
                    i++;
                }
                else{
                    $(form).hide();
                    return
                }
            })
        }
    }
}

class PriceSum{
    constructor(properties){
        this.forms_selector = properties.forms_selector;

        this.quantity_selector = properties.quantity_selector;
        this.price_selector = properties.price_selector;
        this.sum_price_selector = properties.sum_price_selector;

        this.tax_rate_selector = properties.tax_rate_selector;
        this.sum_tax_rate_selector = properties.sum_tax_rate_selector;

        this.all_sum = $(properties.all_sum);

        this.add_form_btn = $(properties.add_form_btn);

        this.add_form_btn.on('click', this.get_elements.bind(this));
        this.get_elements();
    }

    get_elements(){

        let self = this;

        let forms = $(this.forms_selector);

        $.each(forms, function(ind, form){
            form = $(form);
            form.off('keyup').on('keyup', self.get_sum.bind(self, form));
            form.off('click').on('click', self.get_sum.bind(self, form));
        })
    }

    get_sum(form){

        let quantity = form.find(this.quantity_selector);
        let price = form.find(this.price_selector);
        let sum_price = form.find(this.sum_price_selector);

        let tax_rate = form.find(this.tax_rate_selector);
        let sum_tax_rate = form.find(this.sum_tax_rate_selector)

        if (quantity.val() != '' && price.val() != ''){
            sum_price.html(quantity.val() * price.val());
        }
        else{
            sum_price.html('-');
        }

        if (sum_price.html() != '-' && tax_rate.val() != ''){
            sum_tax_rate.html(parseInt(sum_price.html())*tax_rate.val()/100);
        }
        else{
            sum_tax_rate.html('-');
        }

        this.get_all_sum();
    }

    get_all_sum(){

        let self = this

        let sums = $(this.sum_price_selector);
        let all_sum_val = 0;
        
        $.each(sums, function(ind, value){
            if ($(value).html() != '-'){
                all_sum_val += parseInt($(value).html());
            }
        })

        if (all_sum_val == 0){
            this.all_sum.val('');
        }
        else{
            this.all_sum.val(all_sum_val);
        }
    }
}