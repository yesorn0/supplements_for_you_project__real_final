import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import pickle
import os

MAX_PRODUCTS = 48
MAX_REVIEW_PAGES = 50

categories = {
    '여성 종합비타민': 'https://kr.iherb.com/c/multivitamins?_gl=1*1svu9t*_up*MQ..&cids=1783&sr=2',
    '남성 종합비타민': 'https://kr.iherb.com/c/multivitamins?_gl=1*1svu9t*_up*MQ..&cids=1782&sr=2',
    '임산부 종합비타민': 'https://kr.iherb.com/c/multivitamins?_gl=1*cciqjq*_up*MQ..&cids=100425&sr=2',
    '아연': 'https://kr.iherb.com/c/zinc?_gl=1*jxx4ab*_up*MQ..&sr=2',
    '셀레늄': 'https://kr.iherb.com/c/selenium?_gl=1*1an9tcd*_up*MQ..&sr=2'
}

# ✅ 최적화된 옵션 (headless X, 리소스 차단)
options = uc.ChromeOptions()
options.add_argument("--lang=ko-KR")
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.stylesheets": 2,
    "profile.managed_default_content_settings.fonts": 2
}
options.add_experimental_option("prefs", prefs)

driver = uc.Chrome(options=options)

def load_cookies():
    if os.path.exists("cookies.pkl"):
        driver.get("https://kr.iherb.com")
        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

def save_cookies():
    with open("cookies.pkl", "wb") as f:
        pickle.dump(driver.get_cookies(), f)

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
            element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
            href = element.get_attribute('href')
            if href:
                links.append(href)
        except:
            continue
    return links

def get_ingredient(timeout=2):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="product-overview"]/div/section/div[2]/div/div[1]/div[2]/div/table'))
        )
        return element.text.strip()
    except:
        return '영양성분 없음'

def get_reviews(product_url_id):
    reviews = []
    base_review_url = f"https://kr.iherb.com/r/{product_url_id}?sort=6&isshowtranslated=true&p="

    for page in range(1, MAX_REVIEW_PAGES + 1):
        review_url = base_review_url + str(page)
        driver.get(review_url)

        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'reviews')))
        except:
            print(f"❌ 페이지 {page} 로딩 실패")
            break

        print(f"🔄 리뷰 페이지 {page} 이동 완료: {review_url}")
        page_reviews = 0

        for i in range(1, 11):
            try:
                xpath = f'//*[@id="reviews"]/div[{i}]/div[2]/div/div[4]/a/div/div/span[1]'
                review_element = driver.find_element(By.XPATH, xpath)
                text = review_element.text.strip()
                if text:
                    reviews.append(text)
                    page_reviews += 1
            except:
                continue

        print(f"✅ 페이지 {page} 리뷰 수집: {page_reviews}개")

        if page_reviews == 0:
            print("⛔ 더 이상 리뷰 없음 → 수집 중단")
            break

    return reviews

# ✅ 메인 루프
for supplement, url in categories.items():
    print(f"\n📦 '{supplement}' 카테고리 수집 시작...")
    data = []
    driver.get(url)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    product_links = get_product_links()
    print(f"🔗 수집된 제품 링크 수: {len(product_links)}")

    for idx, link in enumerate(product_links):
        print(f"\n➡️ [{idx+1}/{len(product_links)}] 제품 크롤링 중: {link}")
        try:
            driver.get(link)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            try:
                product = driver.find_element(By.XPATH, '//*[@id="name"]').text
                print(f"📌 제품명: {product}")
            except:
                product = '제품명 없음'
                print("⚠️ 제품명을 찾을 수 없음")

            ingredient = get_ingredient()
            print("✅ 영양성분 로딩 성공" if ingredient != '영양성분 없음' else "⚠️ 영양성분 없음")

            try:
                read_more = driver.find_element(By.XPATH, '//*[@id="product-reviews"]/ugc-pdp-review/ugc-apollo/div/div/div/div/div[2]/ugc-review-list/div/div[6]/ugc-read-more/a/span')
                driver.execute_script("arguments[0].click();", read_more)
                time.sleep(1)
            except:
                pass

            product_id = link.split("/")[-1]
            product_name = link.split("/")[-2]
            review_url_id = f"{product_name}/{product_id}"
            reviews = get_reviews(review_url_id)
            print(f"📝 총 리뷰 수집: {len(reviews)}개")

            def clean_review_text(text):
                return text.replace(',', ' ').replace('\n', ' ').replace('\r', ' ').strip()

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
