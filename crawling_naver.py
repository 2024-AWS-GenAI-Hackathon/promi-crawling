import json
import time
import datetime
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

naver_css = {
    'review_li': 'li.pui__X35jYm.EjjAW',
    'category_fold_a': 'a[data-pui-click-code="keywordmore"]',
    'load_more_XPATH': '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div[3]/div[2]/div/a'
}

# URL
url = 'https://m.place.naver.com/restaurant/1085956231/review/visitor?entry=ple&reviewSort=recent'

# Webdriver headless mode 설정
options = webdriver.ChromeOptions()
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# 새로운 JSON 파일 이름
now = datetime.datetime.now()
file_name = 'naver_review_' + now.strftime('%Y-%m-%d_%H-%M-%S') + '.json'

# 크롤링 시작
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    res = driver.get(url)
    driver.implicitly_wait(30)

    # 페이지 다운
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    try:
        for i in range(15):
            element = driver.find_element(By.XPATH, naver_css['load_more_XPATH'])
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)  # 페이지가 완전히 로드되었는지 기다림
            element.click()
    except Exception as e:
        print('더보기 오류' + str(e))
    else:
        print('더보기 작업 종료')

    time.sleep(25)
    html = driver.page_source
    bs = BeautifulSoup(html, 'lxml')
    reviews = bs.select(naver_css['review_li'])


    # 카테고리 열기
    category_fold_btns = driver.find_elements(By.CSS_SELECTOR, naver_css['category_fold_a'])
    print("카테고리 열기 시작...")
    for button in category_fold_btns:
        try:
            # 버튼이 화면에 보이도록
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(1)

            #(JavaScript로 클릭)
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)

        except Exception as e:
            print(f"클릭 실패: {e}")
    print("카테고리 열기 끝")


    content_id = 1  # content_id 초기값 설정
    reviews_list = []  # 리뷰 데이터 저장 리스트
    for r in reviews:
        # content
        content = r.select_one('div.pui__vn15t2 > a.pui__xtsQN-')

        # posting_time
        date_elements = r.select('div.pui__QKE5Pr > span.pui__gfuUIT > time')
        posting_time = date_elements[0] if date_elements else 'N/A'

        # category
        category_span_elements = r.select('span.pui__jhpEyP')
        print(category_span_elements)

        # 예외 처리
        content = content.text if content else ''
        posting_time = posting_time.text if posting_time else ''

        # 날짜 형식 변환
        try:
            if re.match(r'^\d{1,2}\.\d{1,2}\.\w$', posting_time):
                month, day = posting_time.split('.')[:2]
                posting_time = datetime.datetime.strptime(f'2024.{month}.{day}', '%Y.%m.%d')
            elif re.match(r'^\d{2}\.\d{1,2}\.\d{1,2}\.\w$', posting_time):
                posting_time = datetime.datetime.strptime(posting_time[:8], '%y.%m.%d')
            else:
                posting_time = 'Invalid Date Format'
        except ValueError as e:
            print(f"Date format error for posting_time: {posting_time} - {e}")
            posting_time = 'Invalid Date Format'

        # 카테고리 항목을 모두 가져와서 JSON에 저장
        categories = [category.text for category in category_span_elements] if category_span_elements else ['N/A']

        # 날짜를 문자열로 변환
        posting_time_str = posting_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(posting_time, datetime.datetime) else posting_time

        # 리뷰 데이터를 dict 형태로 준비
        review_data = {
            "content_id": content_id,
            "content": content,

            "posting_time": posting_time_str,  # 날짜를 문자열로 변환하여 저장
            "categories": categories  # 카테고리 리스트 추가
        }

        reviews_list.append(review_data)
        content_id += 1
        time.sleep(0.06)

    # 데이터를 JSON 파일로 저장
    with open(file_name, mode='w', encoding='utf-8') as json_file:
        json.dump(reviews_list, json_file, ensure_ascii=False, indent=4)

    print(f"Data saved to {file_name}")

except Exception as e:
    print(e)
    # 에러 발생 시 빈 리스트 저장
    with open(file_name, mode='w', encoding='utf-8') as json_file:
        json.dump([], json_file, ensure_ascii=False, indent=4)  # 빈 리스트 저장
    print(f"Error occurred. Temporary file saved: {file_name}")
