# 기본 패키지
import re
import time
import pickle
import pandas as pd
from tqdm import tqdm
from tqdm import trange
import warnings
warnings.filterwarnings('ignore')

# 크롤링 패키지
import requests
from selenium import webdriver

# 0. 페이지 한번 맨아래로 내리기
def scroll_bottom():
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")

# 1. 입력한 위치로 설정하기
def set_location(location):
    print(location+'으로 위치 설정 하는중...')
    driver.find_element_by_css_selector('#search > div > form > input').click()
    driver.find_element_by_css_selector('#button_search_address > button.btn-search-location-cancel.btn-search-location.btn.btn-default > span').click()
    driver.find_element_by_css_selector('#search > div > form > input').send_keys(location)
    driver.find_element_by_css_selector('#button_search_address > button.btn.btn-default.ico-pick').click()
    time.sleep(2)
    print(location+'으로 위치 설정 완료!')
    
# 2-1. 카테고리 페이지 Element Number Dictionary 정의
food_dict = { '치킨':5 }

# 2-2. 카테고리 페이지로 넘어가기
def go_to_category(category):
    print(category+' 카테고리 페이지 로드중...')
    driver.find_element_by_xpath('//*[@id="category"]/ul/li[{}]/span'.format(food_dict.get(category))).click()
    time.sleep(3)
    print(category+' 카테고리 페이지 로드 완료!')    

# 3. 카테고리(음식점 리스트) 페이지 모두 펼치기
def stretch_list_page():
    restaurant_count = int(driver.find_element_by_css_selector('#restaurant_count').text)
    scroll_count = int((restaurant_count/20))
    print('모든 음식점 리스트 불러오기 시작...')
    for _ in trange(scroll_count):
        try:
            scroll_bottom()
            time.sleep(3)
        except Exception as e:
            pass
    scroll_bottom()
    time.sleep(3)
    print('모든 음식점 리스트 불러오기 완료!')
    
# 4. 해당 카테고리 음식점 리스트 리턴
def get_restaurant_list():
    restaurant_list=[]
    restaurants = driver.find_elements_by_css_selector('#content > div > div.restaurant-list > div.col-sm-6.contract')
    for restaurant in restaurants:
        restaurant_list.append(restaurant.find_element_by_css_selector('div > table > tbody > tr > td:nth-child(2) > div > div.restaurant-name.ng-binding').text)
    return list(set(restaurant_list))

# 5. 검색창에 음식점 검색하기
def search_restaurant(restaurant_name):
    try:
        driver.find_element_by_xpath('//*[@id="category"]/ul/li[1]/a').click()
        driver.find_element_by_xpath('//*[@id="category"]/ul/li[15]/form/div/input').send_keys(restaurant_name)    
        driver.find_element_by_xpath('//*[@id="category_search_button"]').click()
    except Exception as e:
        print('search_restaurant 에러')
    time.sleep(5)

# 6. 검색한 음식점 클릭
def go_to_restaurant():
    try:
        driver.find_element_by_xpath('//*[@id="content"]/div/div[4]/div[2]/div').click()
    except Exception as e:
        print('go_to_restaurant 에러')
    time.sleep(5)

# 7. 해당 음식점의 리뷰 페이지로 넘어가기
def go_to_review():
    print('리뷰 페이지 로드중...')
    driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[2]/a').click()
    time.sleep(2)
    print('리뷰 페이지 로드 완료!')
    
# 8. 리뷰 더보기 클릭하기 
def click_more_review():
    driver.find_element_by_class_name('btn-more').click()
    time.sleep(2)
    
# 9. 리뷰 페이지 모두 펼치기
def stretch_review_page():
    review_count = int(driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[2]/a/span').text)
    click_count = int((review_count/10))
    print('모든 리뷰 불러오기 시작...')
    for _ in trange(click_count):
        try:
            scroll_bottom()
            click_more_review()
        except Exception as e:
            pass
    scroll_bottom()
    print('모든 리뷰 불러오기 완료!')
        
# 10. 해당 음식점의 모든 리뷰 객체 리턴
def get_all_review_elements():
    reviews = driver.find_elements_by_css_selector('#review > li.list-group-item.star-point.ng-scope')
    return reviews
        
# 11. 페이지 뒤로 가기 (한 음식점 리뷰를 모두 모았으면 다시 음식점 리스트 페이지로 돌아감)
def go_back_page():
    print('페이지 돌아가기중...')
    driver.execute_script("window.history.go(-1)")
    time.sleep(5)
    print('페이지 돌아가기 완료!'+'\n')
    
# 12. 크롤링과 결과 데이터를 pickle 파일로 저장
def save_pickle(location, category, yogiyo_df):
    pickle.dump(yogiyo_df, open('./data/{}_{}_df.pkl'.format(location, category),'wb'))
    print('{} {} pikcle save complete!'.format(location, category))

# 13. 크롤링 메인 함수
def yogiyo_crawling(location, category):
    df = pd.DataFrame(columns=['Restaurant','UserID','Menu','Review',
                                   'Total','Taste','Quantity','Delivery','Date'])
    
    try:
        set_location(location) # 검색할 지역 설정
        go_to_category(category) # 해당 카테고리(음식점 리스트) 페이지로 넘어감

        print('Start [ {} - {} ] Crawling...'.format(location, category))
        
        stretch_list_page() # 카테고리(음식점 리스트) 페이지 모두 펼치기
        restaurant_list = get_restaurant_list() # 해당 카테고리 음식점 리스트 받아오기
        
        for restaurant_name in restaurant_list:
            try:
                print('********** '+restaurant_name+' ( '+str(restaurant_list.index(restaurant_name)+1)
                      +'/'+str(len(restaurant_list))+' 번째) **********')
                
                search_restaurant(restaurant_name) # 음식점을 순서대로 검색
                go_to_restaurant() # 검색한 음식점 클릭             
                go_to_review() # 해당 음식점의 리뷰페이지로 넘어감
                stretch_review_page() # 해당 음식점의 모든 리뷰를 불러옴

                for review in tqdm(get_all_review_elements()):  # 해당 음식점의 리뷰 수 만큼 데이터를 가져옴
                    try:
                        df.loc[len(df)] = { 
                            'Restaurant':driver.find_element_by_class_name('restaurant-name').text,
                            'UserID':review.find_element_by_css_selector('span.review-id.ng-binding').text,
                            'Menu':review.find_element_by_css_selector('div.order-items.default.ng-binding').text,
                            'Review':review.find_element_by_css_selector('p').text,
                            'Total':str(len(review.find_elements_by_css_selector('div > span.total > span.full.ng-scope'))),
                            'Taste':review.find_element_by_css_selector('div:nth-child(2) > div > span.category > span:nth-child(3)').text,
                            'Quantity':review.find_element_by_css_selector('div:nth-child(2) > div > span.category > span:nth-child(6)').text,
                            'Delivery':review.find_element_by_css_selector('div:nth-child(2) > div > span.category > span:nth-child(9)').text,
                            'Date':review.find_element_by_css_selector('div:nth-child(1) > span.review-time.ng-binding').text,
                        }
                    except Exception as e:
                        print('리뷰 페이지 에러')
                        print(e)
                        pass
                    
            except Exception as e:
                print('*** '+restaurant_name+' *** 음식점 페이지 에러')
                go_back_page()
                print(e)
                pass
            
            print('음식점 리스트 페이지로 돌아가는중...')
            go_back_page() # 해당 음식점 리뷰를 모두 모았으면 다시 음식점 리스트 페이지로 돌아감
            
    except Exception as e:
        print('음식점 리스트 페이지 에러')
        print(e)
        pass
        
    print('End of [ {} - {} ] Crawling!'.format(location, category))
    save_pickle(location, category, df) # 해당 음식점 리뷰 데이터를 pickle 파일로 저장함
    
    return df 

# 14. 메인 크롤링 함수
def start_yogiyo_crawling(gu, category):
    dong_list = []
    
    if gu=='동작구':
        dong_list = ['서울특별시 동작구 흑석동 221 중앙대학교']
    elif gu=='송파구':
        dong_list = ['장지동']
    elif gu=='서귀포':
        dong_list = ['제주특별자치도 서귀포시 성산읍 시흥리 1283']

    for dong in dong_list:
        try:
            yogiyo = yogiyo_crawling('{} {}'.format(gu,dong), category)
            print(dong+' - '+category+', shape: '+str(yogiyo.shape)+'\n')
        except Exception as e:
            print('***** '+dong+' 에러 발생 *****')
            print(e)
            pass

# Chrome webdriver - 요기요 메인 페이지 실행
driver = webdriver.Chrome() 
url = 'https://www.yogiyo.co.kr/'
driver.get(url)

start_yogiyo_crawling('동작구','치킨')

df = pickle.load(open('./data/동작구 서울특별시 동작구 흑석동 221 중앙대학교_치킨_df.pkl','rb'))
df.tail()

# Chrome webdriver 종료
driver.close() 
driver.quit() 