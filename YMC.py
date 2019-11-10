import os
import json
import requests # pip install requests
import random
import time
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from fake_useragent import UserAgent # pip install fake-useragent
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Yogiyo:
    HOST = 'https://www.yogiyo.co.kr'
    
    def __init__(self, headers):
        self.headers = headers
        
    def get_restaurant_list_by_geo(self, zip_code,cate):
        url = self.HOST + '/api/v1/restaurants-geo/'
        params = dict(
            items=96,
            order='rank',
            page=0,
            search='',
            zip_code=zip_code,
            cate=cate,
        )
        res = requests.get(url, params=params, headers=self.headers)
        return res.json()
    
    def get_menu_list(self, restaurant_id): # restaurant_id를 지정해주면 그 레스토랑의 메뉴를 가지고 오겠다
        base_url = self.HOST + '/api/v1/restaurants/{restaurant_id}/menu/?add_photo_menu=original'
        url = base_url.format(restaurant_id=restaurant_id)
        res = requests.get(url, headers=self.headers)
        return res.json()

headers = {
    'X-ApiKey': 'iphoneap',
    'X-ApiSecret': 'fe5183cc3dea12bd0ce299cf110a75a2',
    'X-MOD-SBB-CTYPE': 'xhr'
}

yogiyo = Yogiyo(headers)

zip_code = '156070'
restaurants = yogiyo.get_restaurant_list_by_geo('156070','치킨')['restaurants']

df = pd.DataFrame.from_records(restaurants)
df.to_excel('YMC.xlsx')
res_id = df[['id']]
print(len(res_id))


for i in range(len(res_id)):
    id = res_id['id'][i].astype(np.string_).decode('UTF-8')
    url = 'https://www.yogiyo.co.kr/api/v1/restaurants/'+id+'/menu/?add_photo_menu=android'
    res = requests.get(url, headers=headers)
    menu_list = res.json()
    with open('menu_list.json', 'at', encoding='utf8') as f:
        f.write(json.dumps(menu_list, ensure_ascii=False))


'''
url = 'https://www.yogiyo.co.kr/api/v1/restaurants/292688/menu/?add_photo_menu=android'
res = requests.get(url, headers=headers)
menu_list = res.json()

with open('menu_list.xlsx', 'wt', encoding='utf8') as f:
    f.write(json.dumps(menu_list, ensure_ascii=False))

df = pd.DataFrame.from_records(menu_list)
df.to_excel('YMC2_menu.xlsx')
url = 'https://www.yogiyo.co.kr/api/v1/restaurants/292688/menu/?add_photo_menu=android'
res = requests.get(url, headers=headers)
menu_list = res.json()

with open('menu_list.json', 'wt', encoding='utf8') as f:
    f.write(json.dumps(menu_list, ensure_ascii=False))
'''