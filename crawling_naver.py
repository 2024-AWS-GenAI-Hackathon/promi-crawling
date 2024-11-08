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
    'load_more_XPATH': '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div[3]/div[2]/div/a',
    'category_XPATH' : '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div[3]/div[1]/ul/li/div[5]/span'

}
# 카테고리 대분류 
CATEGORY_CHOICE = {
    "food": [
        "음식이 맛있어요",
        "재료가 신선해요",
        "양이 많아요",
        "특별한 메뉴가 있어요",
        "가성비가 좋아요",
        "건강한 맛이에요",
        "반찬이 잘 나와요",
        "메뉴 구성이 알차요",
        "비싼 만큼 가치있어요",
        "기본 안주가 좋아요",
        "술이 다양해요",
        "음료가 맛있어요",
        "커피가 맛있어요",
        "디저트가 맛있어요",
        "코스요리가 알차요",
        "고기 질이 좋아요",
        "현지 맛에 가까워요",
        "향신료가 강하지 않아요",
        "잡내가 적어요"
    ],
    "vibe": [
        "인테리어가 멋져요",
        "매장이 넓어요",
        "뷰가 좋아요",
        "아늑해요",
        "야외공간이 멋져요",
        "컨셉이 독특해요",
        "차분한 분위기에요",
        "대화하기 좋아요",
        "사진이 잘 나와요",
        "음악이 좋아요",
        "집중하기 좋아요",
        "혼술하기 좋아요"
    ],
    "customer": [
        "단체모임 하기 좋아요",
        "혼밥하기 좋아요",
        "반려동물과 가기 좋아요",
        "아이와 가기 좋아요",
        "특별한 날 가기 좋아요"
    ],
    "etc": [
        "친절해요",
        "매장이 청결해요",
        "화장실이 깨끗해요",
        "주차하기 편해요",
        "룸이 잘 되어있어요",
        "오래 머무르기 좋아요",
        "음식이 빨리 나와요",
        "좌석이 편해요",
        "직접 잘 구워줘요",
        "샐러드바가 잘 되어있어요",
        "환기가 잘 돼요",
        "포장이 깔끔해요"
    ]
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

# 날짜 형식 변환
def time_formatter(posting_time):
    try:
        if re.match(r'^\d{1,2}\.\d{1,2}\.\w$', posting_time):
            month, day = posting_time.split('.')[:2]
            posting_time = datetime.datetime.strptime(f'2024.{month}.{day}', '%Y.%m.%d')
        elif re.match(r'^\d{2}\.\d{1,2}\.\d{1,2}\.\w$', posting_time):
            posting_time = datetime.datetime.strptime(posting_time[:8], '%y.%m.%d')
        else:
            posting_time = 'Invalid Date Format'

        return posting_time

    except ValueError as e:
        print(f"Date format error for posting_time: {posting_time} - {e}")
        posting_time = 'Invalid Date Format'

        return posting_time

# 크롤링 시작
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    res = driver.get(url)
    driver.implicitly_wait(30)

    # 페이지 다운
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    try:
        for i in range(1):
            element = driver.find_element(By.XPATH, naver_css['load_more_XPATH'])
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)  # 페이지가 완전히 로드되었는지 기다림
            element.click()
    except Exception as e:
        print('더보기 오류' + str(e))
    else:
        print('더보기 작업 종료')

    print("10초 sleep...")
    time.sleep(10)
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

    # 카테고리 대분류를 찾는 메소드 
    def get_category_classification(text):
        for category, phrases in CATEGORY_CHOICE.items():
            if text in phrases:
                return category
        return "Category not found"  # 일치하는 대분류가 없을 때 기본값

    for r in reviews:
        # content
        content = r.select_one('div.pui__vn15t2 > a.pui__xtsQN-')
        content = content.text if content else ''

        # posting_time
        date_elements = r.select('div.pui__QKE5Pr > span.pui__gfuUIT > time')
        posting_time = date_elements[0] if date_elements else 'N/A'
        posting_time = posting_time.text if posting_time else ''
        posting_time = time_formatter(posting_time)
        posting_time_str = posting_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(posting_time, datetime.datetime) else posting_time    # 문자열로 전환


        # category
        category_span_elements = driver.find_elements(By.XPATH, naver_css['category_XPATH'])
        for element in category_span_elements:
            category_text = element.text
            category_classification = get_category_classification(category_text)

            review_data = {
                "content_id": content_id,
                "content": content,
                "posting_time": posting_time_str,
                "category": category_classification
            }

            reviews_list.append(review_data)
            content_id += 1
            time.sleep(0.06)


    # 데이터를 JSON 파일로 저장
    with open(file_name, mode='w', encoding='utf-8') as json_file:
        json.dump(reviews_list, json_file, ensure_ascii=False, indent=4)

    print(f"Data saved to {file_name}")



# 에러 발생 시 빈 리스트 저장
except Exception as e:
    print(e)
    with open(file_name, mode='w', encoding='utf-8') as json_file:
        json.dump([], json_file, ensure_ascii=False, indent=4)
    print(f"Error occurred. Temporary file saved: {file_name}")


