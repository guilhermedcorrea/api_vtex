import pandas as pd
import requests
import http.client
from dotenv import load_dotenv
import os
import json
import warnings
from itertools import chain

warnings.simplefilter(action='ignore')

load_dotenv()
conn = http.client.HTTPSConnection("api.vtex.com")
TOKEN = os.getenv('TOKEN')
SECRET_KEY = os.getenv('key')
idloja = os.getenv('IDLOJA')

headers = {
            'Accept': "application/json",
            'Content-Type': "application/json",
            'X-VTEX-API-AppKey': f"{SECRET_KEY}",
            'X-VTEX-API-AppToken': f"{TOKEN}"
            }



def calcula_preco(*args, **kwargs):
    for arg in args:
        
        calc =  (arg.get('CANALVENDA',0)/100) + arg.get('BASE PRICE',0) + arg.get('CUSTOENVIO',0) + arg.get('CNT',0)
        print(calc)
        
     
    conn.request("get", f"/t78536/pricing/prices/{arg.get('SKU ID',None)}/", headers=headers)

    res = conn.getresponse()
    data = res.read()

    products = json.loads(data.decode("utf-8"))
    prices = next(chain(products.get('fixedPrices',None)))
    dict_product_prices = {
        "itemId":products.get('itemId',None),
        "listPrice":float(products.get('listPrice',None)),
        "costPrice":float(products.get('costPrice',None)),
        "markup":products.get('markup',None),
        "basePrice":float(products.get('basePrice',None)),
        "tradePolicyId":prices.get('tradePolicyId',None),
        "value":prices.get('value',None),
        "listPrice":prices.get('listPrice',None),
        "minQuantity":prices.get('minQuantity',None)
        
        }
  
    dict_product_prices['new_price'] = round(float(calc),2)
    
    yield dict_product_prices
   


def update_prices_vtex(new_price, idproduct,policyid):

    def get_product_prices(idproduct):
       
        conn.request("get", f"/t78536/pricing/prices/{idproduct}", headers=headers)

        res = conn.getresponse()
        data = res.read()

        dict_prices = json.loads(data.decode("utf-8"))
        prices = {
            "itemId":dict_prices['itemId'],
            "listPrice":dict_prices['listPrice'],
            "costPrice":dict_prices['costPrice'],
            "markup":dict_prices['markup'],
            "basePrice":dict_prices['basePrice'],
            "policyid":policyid,
            "new_price":new_price
            }
        print(prices)
        yield prices
        
    def update_prices(product_prices):
        prices = next(product_prices)


        payload= json.dumps({"markup": 0,"basePrice": prices['basePrice'],"listPrice": prices['listPrice'],
            "fixedPrices": [
                {
                "tradePolicyId": f"{prices['policyid']}",
                "value": prices['new_price'],
                "listPrice": prices['new_price'],
                "minQuantity": 1,
                "dateRange": {
                    "from": "2022-05-21T22:00:00Z",
                    "to": "2023-05-28T22:00:00Z"
                        }
                    }
                ]
            })
        
        conn.request("put", f"/t78536/pricing/prices/{prices['itemId']}", payload, headers)

        res = conn.getresponse()
        data = res.read()
        

    #update_prices(price, idproduct)
    
    product_prices = get_product_prices(idproduct)
    update_prices(product_prices)
   
listas = [{'SKU ID':776,'BASE PRICE':21.00,'CANALVENDA':14,'CUSTOENVIO':0.01,'CNT':2.00},
         {'SKU ID':125,'BASE PRICE':1.99,'CANALVENDA':14,'CUSTOENVIO':0.20,'CNT':2.00},
         {'SKU ID':775,'BASE PRICE':22.00,'CANALVENDA':14,'CUSTOENVIO':1.00,'CNT':2.00}]

for lista in listas:
    prices = calcula_preco(lista)
    
    new_prices = next(prices)
  
    if isinstance(new_prices, dict):
        update_prices_vtex(new_prices['new_price'],new_prices['itemId'],1)

    
  
