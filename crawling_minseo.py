#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    'date': '.x1p4m5qa',
    'follower': '.x9f619.x1n2onr6.x1ja2u2z > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div:nth-child(2) > div > div.x1gryazu.xh8yej3.x10o80wk.x14k21rp.x17snn68.x6osk4m.x1porb0y.x8vgawa > section > main > div > header > section.xc3tme8.x18wylqe.x1xdureb.xvxrpd7.x13vxnyz > ul > li:nth-child(2) > div > a',
    'follower_account': '.xyi19xy.x1ccrb07.xtf3nb5.x1pc53ja.x1lliihq.x1iyjqo2.xs83m0k.xz65tgg.x1rife3k.x1n2onr6 > div:nth-child(2) > div > div > div > div > div > div.x9f619.x1ja2u2z.x78zum5.x1n2onr6.x1iyjqo2.xs83m0k.xeuugli.x1qughib.x6s0dn4.x1a02dak.x1q0g3np.xdl72j9 > div > div > div > div > div > a > div > div > span'
}

account_name_list = ['nike']

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

follower_data = {
    'follower': []
}

# account_name에 접속하여 최근 10개의 posts에서
# 1. 업로드 날짜
# 2. 본문 내용
# 3. 첫번째 이미지
# 4. 좋아요 개수
# 5. 팔로워 계정명들
MAX_POST_lENGTH = 20

for account_name in account_name_list:
    driver.get(f'https://instagram.com/{account_name}/')
    driver.implicitly_wait(10)

    covers = driver.find_elements(By.CSS_SELECTOR, selector['cover'])
    MIN_POST_LENGTH = min(MAX_POST_lENGTH, len(covers))

    for i in range(MIN_POST_LENGTH):
        image.append(covers[i].get_attribute('src'))

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
    for i in range(MIN_POST_LENGTH):
        try:
            text.append(driver.find_element(By.CSS_SELECTOR, selector['text']).text)
        except NoSuchElementException:  # 본문이 없는 게시물 예외 처리
            text.append('')
        count = driver.find_element(By.CSS_SELECTOR, selector['like']).text
        if count == '':
            time.sleep(1)
        like.append(driver.find_element(By.CSS_SELECTOR, selector['like']).text)
        date.append(driver.find_element(By.CSS_SELECTOR, selector['date']).get_attribute('title'))

        if i < MIN_POST_LENGTH - 1:
            next_btn = driver.find_element(By.CSS_SELECTOR, selector['next_btn'])
            next_btn.click()
            driver.implicitly_wait(10)

    # 팔로워 이름들 얻기
    ## 1. 계정 홈으로 돌아감
    driver.get(f'https://instagram.com/{account_name}/')

    ## 2. 팔로워 버튼 눌러 찾기
    follower_btn = driver.find_element(By.CSS_SELECTOR, selector['follower'])
    follower_btn.click()
    driver.implicitly_wait(10)

    ## 3. 팔로워 목록 창 스크롤
    scrollable_popup = driver.find_element(By.XPATH,
                                           "//div[@class='x1dm5mii x16mil14 xiojian x1yutycm x1lliihq x193iq5w xh8yej3']")
    for _ in range(10):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_popup)
        time.sleep(2)

    ## 4. 팔로워 계정 이름 가져오기
    follower_accounts = driver.find_elements(By.CSS_SELECTOR, selector['follower_account'])
    num_followers = min(100, len(follower_accounts))

    for i in range(num_followers):
        try:
            follower_account_name = follower_accounts[i].text
            follower_data['follower'].append(follower_account_name)
        except NoSuchElementException:
            print(f"Follower {i + 1} not found.")
            break



df = pd.DataFrame(data)
df.to_excel('./instagram.xlsx')

print("============================================")
print(df)

df = pd.DataFrame(follower_data)
df.to_excel('./instagram_follower.xlsx')

print("============================================")
print(df)