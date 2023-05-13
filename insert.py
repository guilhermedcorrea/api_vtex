from config import mssql_get_conn


from sqlalchemy import Table
from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, MetaData, Float, Integer,ForeignKey,DateTime, Boolean, String, Column
from datetime import datetime
from sqlalchemy import insert,select
import requests
import http.client
from dotenv import load_dotenv
import os
import json
from itertools import chain

import pandas as pd



load_dotenv()

TOKEN = os.getenv('TOKEN')
SECRET_KEY = os.getenv('key')



engine = mssql_get_conn()
metadata = MetaData()
metadata_obj = MetaData(schema="comercial")

DimPedido = Table(
"controle_precos_vtex",
metadata,
Column('cod_preco',Integer, primary_key=True),
Column('politicaid',Integer),
Column('politicaidprincipal',Integer),
Column('novo_preco',Integer),
Column('preco_base',Integer),
Column('data_alteracao',Integer),
Column('canal_venda',Integer),
Column('custo_envio',Integer),
Column('cnt',Integer),
Column('sku_id',Integer)
,schema="dbo",extend_existing=True)



def inserts(*args):
    for arg in args:
        try:
            with engine.connect() as conn:
                result = conn.execute(insert(DimPedido)
                        ,[{"sku_id":arg["sku_id"],"politicaid":arg["tradePolicyId"],"politicaidprincipal":1
                        ,"preco_base":arg["listPrice"],"canal_venda":4,"novo_preco":arg["listPrice"],"custo_envio":0,"cnt":0}])
        except Exception as e:
            print(e)                               
                                            


conn = http.client.HTTPSConnection("api.vtex.com")



headers = {
    'Accept': "application/json",
    'Content-Type': "application/json",
    'X-VTEX-API-AppKey': f"{SECRET_KEY}",
    'X-VTEX-API-AppToken': f"{TOKEN}"
    }



"""Teste insert"""

data = pd.read_csv(r"C:\api_vtex\preco_produtos.csv",sep=";")
data.head(1)

listas = data['SKU ID'].to_list()

for lista in listas:
    print(lista)
    
    
    conn.request("get", f"https://api.vtex.com/t78536/pricing/prices/{lista}/", headers=headers)

    res = conn.getresponse()
    data = res.read()
    new_dict = {}
    produtos = json.loads(data.decode("utf-8"))
    print(produtos)
    items = next(chain(produtos['fixedPrices']))


    produtos['itemId'],
    new_dict['sku_id'] = int(produtos['itemId'])
    new_dict['tradePolicyId'] = int(items['tradePolicyId'])
    new_dict['value'] = float(items['value'])
    new_dict['listPrice'] = float(items['listPrice'])


    inserts(new_dict)

#print(json.loads(data.decode("utf-8")))

#inserts()
