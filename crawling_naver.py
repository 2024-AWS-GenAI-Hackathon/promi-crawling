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


content_id = 1
reviews_list = []
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
res = driver.get(url)
driver.implicitly_wait(30)

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

        # datetime을 문자열로 변환하여 반환
        return posting_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(posting_time, datetime.datetime) else posting_time

    except ValueError as e:
        print(f"Date format error for posting_time: {posting_time} - {e}")
        return 'Invalid Date Format'

# 카테고리 대분류를 찾는 메소드
def get_category_classification(text):
    for category, phrases in CATEGORY_CHOICE.items():
        if text in phrases:
            return category
    return "Category not found"  # 일치하는 대분류가 없을 때 기본값

# 카테고리 중복 삭제 메소드 
def remove_duplicate_categories(review_data_list):
    seen = set()  # 이미 본 category와 content를 추적할 집합
    unique_reviews = []
    content_id = 1 #아이디 값 초기화

    for review_data in review_data_list:
        # category와 content를 합친 튜플을 중복 체크 기준으로 사용
        category_content = (review_data["category"], review_data["content"])
        
        if category_content not in seen:
            review_data['content_id'] = content_id
            unique_reviews.append(review_data)
            content_id += 1 
            seen.add(category_content)  # 해당 category와 content의 조합 중복임을 기록 

    return unique_reviews


##############################################################################

# 크롤링 시작
try:
    # 페이지 다운
    for i in range(15):
        try:
            more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.fvwqf'))
            )
            driver.execute_script("arguments[0].click();", more_button)
            time.sleep(3)  # 새로운 리뷰 로드 대기
        except Exception as e:
            print("No more pages to load:", e)
            break

    print("10초 sleep...")
    time.sleep(10)
    html = driver.page_source
    bs = BeautifulSoup(html, 'lxml')
    reviews = driver.find_elements(By.CSS_SELECTOR, 'li.pui__X35jYm.EjjAW')

    for r in reviews:
        content = r.find_element(By.CSS_SELECTOR, 'div.pui__vn15t2').text.strip()
        date = r.find_element(By.CSS_SELECTOR, 'span.pui__gfuUIT > time').text.strip()

        # 태그 저장
        i_tags = [tag.text.strip() for tag in r.find_elements(By.CSS_SELECTOR, 'div.pui__HLNvmI')]
        i_tags = str(i_tags)
        if "+" not in i_tags:  # 태그 0개, 1개일 때
            i_tag = [tag.text.strip() for tag in r.find_elements(By.CSS_SELECTOR, 'div.pui__HLNvmI')]
        else:  # 태그 2개 이상일 때
            # 태그 더보기 버튼 누르기
            tag_button = r.find_element(By.CSS_SELECTOR, 'a.pui__jhpEyP.pui__ggzZJ8')
            driver.execute_script("arguments[0].click();", tag_button)
            time.sleep(1)
            # 태그 여러 개 잘라서 리스트에 저장
            i_tag = [tag.text.strip() for tag in r.find_elements(By.CSS_SELECTOR, 'div.pui__HLNvmI span.pui__jhpEyP')]

        for tag in i_tag:
            review_data = {
                # "content_id": content_id,
                "content": content,
                "posting_time": time_formatter(date),
                "category": get_category_classification(tag),    
            }

            reviews_list.append(review_data)
            # content_id += 1
            time.sleep(0.06)

    # 중복된 category 제거
    reviews_list = remove_duplicate_categories(reviews_list)

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


