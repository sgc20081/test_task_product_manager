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
    
    table = pa.Table.from_pydict(data)

    # Записываем таблицу в поток.
    stream = io.BytesIO()
    pq.write_table(table, stream)

    # Возвращаем строку из потока.
    stream.getvalue()
    string_parquet = stream.getvalue()

    # print(parquet_string)

    return HttpResponse(string_parquet)