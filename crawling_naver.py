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
from selenium.webdriver.common.by import By


# url
url = 'https://m.place.naver.com/restaurant/1085956231/review/visitor?entry=ple&reviewSort=recent'

# Webdriver headless mode setting
options = webdriver.ChromeOptions()
# options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# New JSON file
now = datetime.datetime.now()
file_name = 'naver_review_' + now.strftime('%Y-%m-%d_%H-%M-%S') + '.json'

# Start crawling/scraping!
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    res = driver.get(url)
    driver.implicitly_wait(30)

    # Pagedown
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)

    try:
        for i in range(30):  # 최대 30번 반복
            element = driver.find_element(By.XPATH,
                                          '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div[3]/div[1]/ul/li[2]/div[5]/a')
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)  # Wait a bit to ensure it has fully scrolled into view
            element.click()
    except Exception as e:
        print('더보기 오류' + str(e))
    else:
        print('더보기 버튼 눌림 작업 종료')

    time.sleep(25)
    html = driver.page_source
    bs = BeautifulSoup(html, 'lxml')
    reviews = bs.select('li.pui__X35jYm.EjjAW')

    # 카테고리 모두 열기
    try:
        # Wait for element to be clickable
        category_fold_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div[3]/div[1]/ul/li[2]/div[5]/a'))
        )

        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", category_fold_btn)
        time.sleep(1)  # Ensure it's fully visible

        # Click the button using JavaScript to bypass overlay issues
        driver.execute_script("arguments[0].click();", category_fold_btn)
        print("Category fold button clicked successfully")
    except Exception as e:
        print(f"Error while clicking the element: {e}")

    content_id = 1  # content_id 초기값 설정

    reviews_list = []  # List to store review data

    for r in reviews:
        # content
        content = r.select_one('div.pui__vn15t2 > a.pui__xtsQN-')

        # posting_time
        date_elements = r.select('div.pui__QKE5Pr > span.pui__gfuUIT > time')
        posting_time = date_elements[0] if date_elements else 'N/A'

        # category
        category_span_elements = r.select('span.pui__jhpEyP')

        # exception handling
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

        # Prepare review data in dict format
        review_data = {
            "content_id": content_id,
            "content": content,
            "posting_time": posting_time,
            "category": category_span_elements[0].text if category_span_elements else 'N/A'
        }

        reviews_list.append(review_data)

        content_id += 1
        time.sleep(0.06)

    # Save data to JSON file
    with open(file_name, mode='w', encoding='utf-8') as json_file:
        json.dump(reviews_list, json_file, ensure_ascii=False, indent=4)

    print(f"Data saved to {file_name}")

except Exception as e:
    print(e)
    # Save the file(temp) in case of error
    with open(file_name, mode='w', encoding='utf-8') as json_file:
        json.dump([], json_file, ensure_ascii=False, indent=4)  # Empty list in case of error
    print(f"Error occurred. Temporary file saved: {file_name}")
