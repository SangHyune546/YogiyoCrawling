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
    
    #요기요 내부 zip 코드로 해당 위치의 음식점 리스트 불러오기
    def get_restaurant_list_by_geo(self, zip_code,cate):
        url = self.HOST + '/api/v1/restaurants-geo/'
        params = dict(
            items=96,
            order='rank',
            page=0,
            search='',
            zip_code=zip_code,
            cate=cate,
        ) #cate = category 치킨, 피자 등 음식 카테고리 지정
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
} #url에 붙여서 전송할 header

yogiyo = Yogiyo(headers) #yogiyo 객체 함수로 url get
zip_code = '156070' # 서울특별시 동작구 흑석동 221 중앙대학교 의 요기요 내부 zipcode

restaurants = yogiyo.get_restaurant_list_by_geo('156070','치킨')['restaurants'] # 156070위치의 치킨 카테고리에 있는 음식점 크롤링

df = pd.DataFrame.from_records(restaurants) # 음식점 목록의 pandas dataframe 화
df.to_excel('YMC.xlsx') # 음식점 목록 xlsx파일로 저장

res_id = df[['id']] # 음식점 목록 df에서 음식점의 id 열 추출
print(len(res_id)) # 음식점 목록의 개수 출력 (중앙대 기준 치킨카테고리의 음식점 : 96개)

# 총 음식점 개수만큼 각 음식점의 메뉴 추츨 후 json파일로 저장. 음식점 id로 각 음식점 식별
for i in range(len(res_id)):
    id = res_id['id'][i].astype(np.string_).decode('UTF-8')
    url = 'https://www.yogiyo.co.kr/api/v1/restaurants/'+id+'/menu/?add_photo_menu=android'
    res = requests.get(url, headers=headers)
    menu_list = res.json()
    with open('menu_list.json', 'at', encoding='utf8') as f:
        f.write(json.dumps(menu_list, ensure_ascii=False))
        
