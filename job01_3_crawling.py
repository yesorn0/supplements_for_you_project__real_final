import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd
import time
import pickle
import os

MAX_PRODUCTS = 2
MAX_REVIEW_PAGES = 10

categories = {
    '여성 종합비타민': 'https://kr.iherb.com/c/multivitamins?_gl=1*1svu9t*_up*MQ..&cids=1783&sr=2',
    '남성 종합비타민': 'https://kr.iherb.com/c/multivitamins?_gl=1*1svu9t*_up*MQ..&cids=1782&sr=2',
    '임산부 종합비타민': 'https://kr.iherb.com/c/multivitamins?_gl=1*cciqjq*_up*MQ..&cids=100425&sr=2',
    '아연': 'https://kr.iherb.com/c/zinc?_gl=1*jxx4ab*_up*MQ..&sr=2',
    '셀레늄': 'https://kr.iherb.com/c/selenium?_gl=1*1an9tcd*_up*MQ..&sr=2'
}

options = uc.ChromeOptions()
options.add_argument("--lang=ko-KR")
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=options)

# 쿠키 로드 함수
def load_cookies():
    if os.path.exists("cookies.pkl"):
        driver.get("https://kr.iherb.com")
        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(3)

# 쿠키 저장 함수
def save_cookies():
    with open("cookies.pkl", "wb") as f:
        pickle.dump(driver.get_cookies(), f)

# 실행 시 수동으로 캡차 통과 후 쿠키 저장 안내
if not os.path.exists("cookies.pkl"):
    print("❗ CAPTCHA 페이지가 보이면 직접 수동으로 풀고 Enter를 누르세요...")
    driver.get("https://kr.iherb.com")
    input("👉 캡차를 통과했으면 Enter 키를 누르세요...")
    save_cookies()
else:
    load_cookies()

def get_product_links():
    links = []
    for i in range(1, MAX_PRODUCTS + 1):
        try:
            xpath = f'/html/body/div[7]/div/div[3]/div/div/div[1]/div[1]/div[3]/div[{i}]/div/div[2]/div[1]/a'
            element = driver.find_element(By.XPATH, xpath)
            href = element.get_attribute('href')
            if href:
                links.append(href)
        except:
            continue
    return links

def get_reviews():
    reviews = []
    for page in range(1, MAX_REVIEW_PAGES + 1):
        for i in range(1, 11):
            try:
                xpath = f'//*[@id="reviews"]/div[{i}]/div[2]/div/div[4]/a/div/div/span[1]'
                review_element = driver.find_element(By.XPATH, xpath)
                text = review_element.text.strip()
                if text:
                    reviews.append(text)
            except:
                continue
        # 페이지 이동 버튼 XPath
        try:
            if page == 1:
                next_button_xpath = '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[8]/nav/ul/li[3]/button'
            elif page == 2:
                next_button_xpath = '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[8]/nav/ul/li[4]/button'
            elif page == 3:
                next_button_xpath = '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[8]/nav/ul/li[5]/button'
            else:  # 4페이지부터는 li[6]/button 고정
                next_button_xpath = '//*[@id="__next"]/div[2]/div[2]/div/div[2]/div[8]/nav/ul/li[6]/button'
            next_button = driver.find_element(By.XPATH, next_button_xpath)
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
        except:
            break
    return reviews

for supplement, url in categories.items():
    data = []  # 카테고리별 데이터 초기화
    driver.get(url)
    time.sleep(3)
    product_links = get_product_links()

    for link in product_links:
        try:
            driver.get(link)
            time.sleep(2)

            try:
                product = driver.find_element(By.XPATH, '//*[@id="name"]').text
            except:
                product = '제품명 없음'

            try:
                ingredient = driver.find_element(By.XPATH, '//*[@id="product-overview"]/div/section/div[2]/div/div[1]/div[2]/div/table').text
            except:
                ingredient = '영양성분 없음'

            try:
                read_more = driver.find_element(By.XPATH, '//*[@id="product-reviews"]/ugc-pdp-review/ugc-apollo/div/div/div/div/div[2]/ugc-review-list/div/div[6]/ugc-read-more/a/span')
                driver.execute_script("arguments[0].click();", read_more)
                time.sleep(2)
            except:
                pass

            reviews = get_reviews()

            for rev in reviews:
                data.append({
                    'supplements': supplement,
                    'product': product,
                    'ingredient': ingredient,
                    'review': rev
                })

        except Exception as e:
            print(f"[오류] {link} - {e}")
            continue

    # 카테고리별로 CSV 저장
    df = pd.DataFrame(data)
    filename = f'iherb_uc_{supplement}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✅ {supplement} 카테고리 저장 완료 → {filename}")

# 종료 처리
driver.quit()
print("🔚 전체 크롤링 완료")


