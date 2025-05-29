import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd
import time
import pickle
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

MAX_PRODUCTS = 2
MAX_REVIEW_PAGES = 6

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

# 제품 링크 수집 함수
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

# 영양정보 수집 함수
def get_ingredient(timeout=1):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="product-overview"]/div/section/div[2]/div/div[1]/div[2]/div/table'))
        )
        return element.text.strip()
    except:
        return '영양성분 없음'

# 리뷰 수집 함수 (URL 방식)
def get_reviews(product_url_id):
    reviews = []
    base_review_url = f"https://kr.iherb.com/r/{product_url_id}?sort=6&isshowtranslated=true&p="

    for page in range(1, MAX_REVIEW_PAGES + 1):
        review_url = base_review_url + str(page)
        driver.get(review_url)
        time.sleep(2)

        found_any = False
        for i in range(1, 11):
            try:
                xpath = f'//*[@id="reviews"]/div[{i}]/div[2]/div/div[4]/a/div/div/span[1]'
                review_element = driver.find_element(By.XPATH, xpath)
                text = review_element.text.strip()
                if text:
                    reviews.append(text)
                    found_any = True
            except:
                continue

        if not found_any:
            break
    return reviews

# 카테고리별 수집 루프
for supplement, url in categories.items():
    print(f"\n📦 '{supplement}' 카테고리 수집 시작...")
    data = []
    driver.get(url)
    time.sleep(3)
    product_links = get_product_links()
    print(f"🔗 수집된 제품 링크 수: {len(product_links)}")

    for idx, link in enumerate(product_links):
        print(f"\n➡️ [{idx+1}/{len(product_links)}] 제품 크롤링 중: {link}")
        try:
            driver.get(link)
            time.sleep(2)

            try:
                product = driver.find_element(By.XPATH, '//*[@id="name"]').text
                print(f"📌 제품명: {product}")
            except:
                product = '제품명 없음'
                print("⚠️ 제품명을 찾을 수 없음")

            ingredient = get_ingredient()
            if ingredient == '영양성분 없음':
                print("⚠️ 영양성분 로딩 실패 또는 없음")
            else:
                print("✅ 영양성분 로딩 성공")

            product_id = link.split("/")[-1]
            product_name = link.split("/")[-2]
            review_url_id = f"{product_name}/{product_id}"

            reviews = get_reviews(review_url_id)
            print(f"📝 수집된 리뷰 수: {len(reviews)}")

            def clean_review_text(text):
                text = text.replace(',', ' ').replace('\n', ' ').replace('\r', ' ')
                return text.strip()

            cleaned_reviews = [clean_review_text(r) for r in reviews]
            review_combined = ' | '.join(cleaned_reviews)

            data.append({
                'supplements': supplement,
                'product': product,
                'ingredient': ingredient,
                'review': review_combined
            })

        except Exception as e:
            print(f"[❌ 오류] {link} - {e}")
            continue

    df = pd.DataFrame(data)
    filename = f'iherb_uc_{supplement}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✅ '{supplement}' 카테고리 저장 완료 → {filename}")

driver.quit()
print("🔚 전체 크롤링 완료")
