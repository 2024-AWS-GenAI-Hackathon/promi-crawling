from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook
import datetime
import time

# WebDriver 설정
options = Options()
options.add_argument("window-size=1920x1080")
service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://m.place.naver.com/restaurant/1008629511/review/visitor?reviewSort=recent")
driver.implicitly_wait(10)

# 엑셀 파일 설정
now = datetime.datetime.now()
xlsx = Workbook()
list_sheet = xlsx.create_sheet('output')
list_sheet.append(['content', 'date', 'tags'])

# 전체 더보기 버튼 클릭하여 모든 리뷰 로드
try:
    for i in range(1):
        try:
            more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.fvwqf'))
            )
            driver.execute_script("arguments[0].click();", more_button)
            time.sleep(3)  # 새로운 리뷰 로드 대기
        except Exception as e:
            print("No more pages to load:", e)
            break

    # 모든 페이지가 로드되었으므로, 이제 리뷰 데이터와 태그를 수집
    reviews = driver.find_elements(By.CSS_SELECTOR, 'li.pui__X35jYm.EjjAW')

    for r in reviews:
        nickname = r.find_element(By.CSS_SELECTOR, 'span.pui__uslU0d').text.strip()
        content = r.find_element(By.CSS_SELECTOR, 'div.pui__vn15t2').text.strip()
        date = r.find_element(By.CSS_SELECTOR, 'span.pui__gfuUIT > time').text.strip()
        revisit_elements = r.find_elements(By.CSS_SELECTOR, 'span.pui__gfuUIT')
        revisit = revisit_elements[1].text.strip() if len(revisit_elements) > 1 else ''
        review_cnt = r.find_element(By.CSS_SELECTOR, 'span.pui__WN-kAf').text.strip()
        url = r.find_element(By.CSS_SELECTOR, 'a[href*="/my"]').get_attribute('href')

        # revisit "번째 방문" 문자 제거
        if revisit:
            revisit = int(revisit[:-5])

        # review_cnt "리뷰 " 문자 제거
        if review_cnt:
            review_cnt = int(review_cnt[3:])

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

        # 중복 없이 리뷰 데이터 저장
        list_sheet.append([content, date, ", ".join(i_tag)])

except Exception as e:
    print('Error:', e)
finally:
    # Excel 파일 저장 및 드라이버 종료
    file_name = f'naver_review_{now.strftime("%Y-%m-%d_%H-%M-%S")}.xlsx'
    xlsx.save(file_name)
    driver.quit()

print("Data collection completed and saved to Excel.")