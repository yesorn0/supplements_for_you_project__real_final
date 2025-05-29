from selenium import webdriver #웹 자동화 라이브러리
from selenium.webdriver.common.by import By # 요소 찾기 방식(id, class, xpath 등)
from selenium.webdriver.common.keys import Keys # 키보드 입력을 다루기 위한 모듈
from selenium.webdriver.chrome.service import Service as ChromeService # 크롬드라이버 실행 관련 설정
from selenium.webdriver.chrome.options import Options as ChromeOptions # 크롬 실행 옵션 설정
from setuptools.package_index import user_agent
from webdriver_manager.chrome import ChromeDriverManager # 자동으로 크롬 드라이버 설치
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException # 예외 처리용
import pandas as pd # 데이터프레임 처리용
import re # 정규 표현식 처리용
import time # 시간 지연
import datetime # 시간 관련 함수
from selenium_stealth import stealth
from playwright.sync_api import sync_playwright
import random


# -----------------------------------------------------------
urls = [
    ('여성 종합비타민', 'https://kr.iherb.com/c/multivitamins?_gl=1*1svu9t*_up*MQ..&cids=1783&sr=2')
    # ('남성 종합비타민', 'https://kr.iherb.com/c/multivitamins?_gl=1*1svu9t*_up*MQ..&cids=1782&sr=2'),
    # ('임산부 종합비타민', 'https://kr.iherb.com/c/multivitamins?_gl=1*cciqjq*_up*MQ..&cids=100425&sr=2'),
    # ('아연', 'https://kr.iherb.com/c/zinc?_gl=1*jxx4ab*_up*MQ..&sr=2'),
    # ('셀레늄', 'https://kr.iherb.com/c/selenium?_gl=1*1an9tcd*_up*MQ..&sr=2')
]

# 1. 크롬 옵션 구현
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36 Edg/122.0.2365.66",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36",
]

# url 접속 후, 제품의 id 수집, 순차적으로 접속하여 크롤링
results = []
with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ua = random.choice(user_agents)  # 랜덤 유저에이전트 선택
        context = browser.new_context(locale="ko-KR", user_agent=ua)
        page = context.new_page()

        # 1. 상품 링크 수집.
        product_links = []
        for name, url in urls:
                page.goto(url, timeout=20000)
                # 상품 박스 수집: id가 'pid_'로 시작하는 모든 div
                product_divs = page.query_selector_all("div[id^='pid_']")
                for div in product_divs:
                        pid = div.get_attribute("id") # pid_125281형태
                        a_tag = div.query_selector("div:nth-child(2) > div:nth-child(1) > a")
                        if a_tag:
                                href = a_tag.get_attribute("href")
                                if href:
                                        full_url = href
                                        product_links.append((pid, full_url))
                print(f"✅ 수집된 상품 수: {len(product_links)}")
                product_links = product_links[:40]  # 최대 40개까지만 사용

        # 2. 각 제품 상세 페이지 접속
        supplements = []  # 영양제 종류 저장용
        product = []  # 제품이름 저장용
        ingredient = []  # 영양성분 저장용
        for _, link in product_links:
                page.goto(link, timeout=20000)
                try:
                        name = page.locator('//*[@id="name"]').inner_text(timeout=3000)
                except:
                        name = "N/A"

                try:
                        overview = page.locator(
                                '//*[@id="product-overview"]/div/section/div[2]/div/div[1]/div[2]/div').inner_text(
                                timeout=3000)
                except:
                        overview = "N/A"

        # 3. 리뷰페이지 접속 및 리뷰 수집(최대 500개 까지)
                review = []  # 리뷰 저장용
                base_review_url = link.replace("/pr/", "/r/")
                for page_num in range(1, 4): # 테스트로 3 페이지만 실행
                    review_url = f"{base_review_url}?sort=6&isshowtranslated=true&p={page_num}"
                    page.goto(review_url, timeout=20000)
                    for i in range(1, 11):
                        try:
                            xpath = f'//*[@id="reviews"]/div[{i}]/div[2]/div/div[4]/a/div/div/span[1]'
                            text = page.locator(xpath).inner_text(timeout=2000)
                            review.append(text)
                        except:
                            continue
                results.append(
                        {
                                "영양제 종류": supplements,
                                "제품명": product,
                                "영양성분": ingredient,
                                "리뷰": review
                            })


        browser.close()

# 데이터 프레임으로 저장하고 csv로 내보내기
df = pd.DataFrame(results)
df.to_csv('./crawling_data/reviews.csv', index=False) # CSV저장
print("")


# hrefs = []
# titles = []
# for i in range(1, 100):
#     # 영화 상세 페이지 링크 추출
#     href = driver.find_element(By.XPATH,
#             '/html/body/div/div/div/main/div/div[2]/a[{}]'.format(i)).get_attribute('href')
#     hrefs.append(href)
#
#     # 영화 제목 추출
#     title = driver.find_element(By.XPATH,
#             '/html/body/div/div/div/main/div/div[2]/a[{}]/div/div[2]/span'.format(i)).text
#     titles.append(title)
# print(hrefs) # 링크 리스트 출력
# print(titles) # 제목 리스트 출력
#
# # -----------------------------------------------------------
# # 리뷰 페이지 진입 및 내용
#
# reviews = [] # 전체 영화 리뷰 저장용
# for idx, url in enumerate(hrefs):
#     driver.get(url + '?tab=review') 리뷰 탭으로 이동
#     time.sleep(0.5)
#     # 리뷰가 있는 영역 스크롤
#     scroll_to_bottom(scroll_target_xpath='//*[@id="content__body"]', times=5)
#
#     review = '' # 현재 영화의 리뷰 모음
#     for i in range(1, 10):  # 리뷰 9개까지 시도
#         try:
#             # 더보기 버튼 클릭
#             review_xpath = '//*[@id="contents"]/div[4]/section[2]/div/article[{}]/div[3]/a[2]'.format(i)
#             review_button = driver.find_element(By.XPATH, review_xpath)
#             driver.execute_script('arguments[0].click();', review_button)
#             time.sleep(0.5)
#             try:
#                 # 상세 리뷰 본문 추출
#                 review = review + driver.find_element(By.XPATH,
#                       '//*[@id="contents"]/div[2]/div[1]/div/section[2]/div/div/div/p').text
#             except:
#                 # 다른 구조일 경우 h3태그에서 가져옴
#                 review = review + driver.find_element(By.XPATH,
#             '//*[@id="contents"]/div[2]/div[1]/div/section[2]/div/div/h3').text
#             driver.back() # 다시 리뷰 목록으로 돌아감
#             print(i, 'try')
#         except:
#             try:
#                 # 더보기 없이 바로 보이는 리뷰 수정
#                 review = review + driver.find_element(By.XPATH,
#                   '//*[@id="contents"]/div[4]/section[2]/div/article[{}]/div[3]/a/h5'.format(
#                               i)).text
#                 print(review)
#                 print(i, 'NoSuchElementException')
#
#             except:
#                 # 해당 위치에 리뷰가 없을 경우 예외
#                 review = review
#                 print(i, 'except')
#
#     reviews.append(review) # 리뷰 저장
# print(reviews)  # 전체 리뷰 출력
#
# # -----------------------------------------------------------
# # 데이터 프레임으로 저장하고 csv로 내보내기
# df = pd.DataFrame({'titles':titles, 'reviews':reviews}) # 제목과 리뷰로 데이터 프레임 생성
# my_name = 'JKY' # 사용자 이름
# df.to_csv('./data/reviews_{}.csv'.format(my_name), index=False) # CSV저장
#
# print("")


# # 브라우저 접속 확인용
# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#
#     for name, url in urls:
#         # 랜덤 유저에이전트 선택
#         ua = random.choice(user_agents)
#
#         context = browser.new_context(locale="ko-KR", user_agent=ua)
#         page = context.new_page()
#
#         print(f"\n🌐 '{name}' 접속 중 (User-Agent: {ua})")
#         page.goto(url, timeout=20000)
#
#         input("👀 확인 후 엔터를 누르세요...")
#
#         context.close()
#
#     browser.close()

# # -----------------------------------------------------------





