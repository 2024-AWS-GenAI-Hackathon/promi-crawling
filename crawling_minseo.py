import time, os
from dotenv import load_dotenv
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


selector = {
    'id_input': '._aa4b._add6._ac4d._ap35',
    'first_post': '._ac7v div a ._aagu > ._aagv + ._aagw',
    'next_btn': '._aaqg._aaqh > ._abl-',
    'cover': 'a ._aagu ._aagv img',
    'text': 'h1._ap3a._aaco._aacu._aacx._aad7._aade',
    'like': 'span a span .html-span.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1hl2dhg.x16tdsg8.x1vvkbs',
    'date': '.x1p4m5qa'
}

account_name_list = ['nike', 'chanelofficial']

load_dotenv(verbose=True)
INSTAGRAM_ID = os.getenv('INSTAGRAM_ID')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

options = webdriver.ChromeOptions()
options.add_argument(
    'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
driver = webdriver.Chrome()

driver.get('https://instagram.com')
driver.implicitly_wait(10)
driver.maximize_window()


def click_nxt():
    next_btn = driver.find_element(By.CSS_SELECTOR, selector['next_btn'])
    next_btn.click()
    driver.implicitly_wait(10)


# 인스타그램 로그인하기
el = driver.find_elements(By.CSS_SELECTOR, selector['id_input'])  # ID input태그 선택하기
el[0].send_keys(INSTAGRAM_ID)
el[1].send_keys(INSTAGRAM_PASSWORD)
el[1].send_keys(Keys.ENTER)
time.sleep(10)

text = []
image = []
like = []
date = []

data = {
    'text': text,
    'image': image,
    'like': like,
    'date': date
}

# account_name에 접속하여 최근 10개의 posts에서
# 1. 업로드 날짜
# 2. 본문 내용
# 3. 첫번째 이미지
# 4. 좋아요 개수
for account_name in account_name_list:
    driver.get(f'https://instagram.com/{account_name}/')
    driver.implicitly_wait(10)

    images = []
    covers = driver.find_elements(By.CSS_SELECTOR, selector['cover'])
    cover_count = len(covers)
    for i in range(min(10, cover_count)):  # 커버 수가 10개 미만일 경우 대비
        images.append(covers[i].get_attribute('src'))
    image.extend(images)

    # 첫 번째 게시물 클릭
    posts = driver.find_elements(By.CSS_SELECTOR, selector['first_post'])
    if posts:
        post = posts[0]
        post.click()
        driver.implicitly_wait(10)
    else:
        print(f"No posts found for brand: {account_name}")
        continue

    # 게시물에서 본문/좋아요수/날짜 얻기
    for i in range(10):
        try:
            text.append(driver.find_element(By.CSS_SELECTOR, selector['text']).text)
        except NoSuchElementException:  # 본문이 없는 게시물 예외 처리
            text.append('')
        count = driver.find_element(By.CSS_SELECTOR, selector['like']).text
        if count == '':
            time.sleep(1)
        like.append(driver.find_element(By.CSS_SELECTOR, selector['like']).text)
        date.append(driver.find_element(By.CSS_SELECTOR, selector['date']).get_attribute('title'))

        if i < 9:
            next_btn = driver.find_element(By.CSS_SELECTOR, selector['next_btn'])
            next_btn.click()
            driver.implicitly_wait(10)

data.update({'image': image})

df = pd.DataFrame(data)
df.set_index(keys=['date'], inplace=True, drop=True)
df.to_excel('./instagram.xlsx')

print(df)
time.sleep(10)