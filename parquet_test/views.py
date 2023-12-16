from django.shortcuts import render
from django.http import HttpResponse

import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

import base64
import io

# Create your views here.

def parquet_get_test(request, *args, **kwargs):

    print('Запущен метод получения Arrow Parquet ответ')

    data = {'column1': [1, 2, 3], 'column2': ['A', 'B', 'C'], 'column3': ['q', 'w', 'e']}
    
    df = pd.DataFrame(data)

    # Преобразуйте DataFrame в таблицу PyArrow
    table = pa.Table.from_pandas(df)

     # Создаем буфер для записи Parquet-файла
    buf = io.BytesIO()
    # Записываем таблицу в формат Parquet в буфер
    pq.write_table(table, buf)

    # Получаем содержимое буфера
    buffer = buf.getvalue()

    return HttpResponse(buffer)