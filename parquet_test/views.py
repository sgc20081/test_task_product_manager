from django.shortcuts import render
from django.http import HttpResponse

import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

import base64

# Create your views here.

def parquet_get_test(request, *args, **kwargs):

    print('Запущен метод получения Arrow Parquet ответ')

    data = {'column1': [1, 2, 3], 'column2': ['A', 'B', 'C'], 'column3': ['q', 'w', 'e']}
    
    # Создаем DataFrame из словаря data
    df = pd.DataFrame(data)

    # Преобразуем DataFrame в Arrow Table
    table = pa.Table.from_pandas(df)

    buffer = pa.BufferOutputStream()
    pq.write_table(table, buffer)
    
    # Получить строку из буфера
    buffer = buffer.getvalue().to_pybytes()
    # file = pq.ParquetFile(buffer)
    # print(file)
    # parquet_string = base64.b64encode(file).decode('utf-8')

    # print(parquet_string)

    return HttpResponse(buffer, content_type='text/plain')