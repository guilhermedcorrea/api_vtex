```Python
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
```


<br>Faz a requisição e obtem informações de preço, preço base e politica comercial do produto. Cria um dicionario e calcula o novo valor com base na porcentagem do Marketplace e retorna com yield<br/>


```Python
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
```
<br>Faz a requisição para a politica comercial principal 1, obtem os preços, usando a referencia do SKU que foi passada, cria um novo dicionarion e retorna para a função que ira fazer as atualizações<br/>




```Python
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
```

<br>Recebe a referencia, novo preço, preço da politica comercial principal, id da politica comercial principal, e o id da politica comericial que tera o preço alterado, envia as atualizações através do 'PUT'<br/>


<br>Ainda irei fazer melhorias nesse codigo. Esta em faze de desenvolvimento e testes<br/>