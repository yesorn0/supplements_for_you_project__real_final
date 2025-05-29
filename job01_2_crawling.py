import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

def load_cookies():
    if os.path.exists("cookies.pkl"):
        driver.get("https://kr.iherb.com")
        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(3)

def save_cookies():
    with open("cookies.pkl", "wb") as f:
        pickle.dump(driver.get_cookies(), f)

if not os.path.exists("cookies.pkl"):
    print("❗ CAPTCHA 페이지가 보이면 수동으로 풀고 Enter를 누르세요...")
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

def get_ingredient(timeout=1):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="product-overview"]/div/section/div[2]/div/div[1]/div[2]/div/table'))
        )
        return element.text.strip()
    except:
        return '영양성분 없음'

def get_reviews(product_name, product_id):
    reviews = []

    review_url = f"https://kr.iherb.com/r/{product_name}/{product_id}?sort=6&isshowtranslated=true&p=1"
    driver.get(review_url)
    time.sleep(2)

    for current_page in range(1, MAX_REVIEW_PAGES + 1):
        print(f"📄 리뷰 페이지 {current_page} 수집 중...")

        for i in range(1, 11):
            try:
                xpath = f'//*[@id="reviews"]/div[{i}]/div[2]/div/div[4]/a/div/div/span[1]'
                review_element = driver.find_element(By.XPATH, xpath)
                text = review_element.text.strip()
                if text:
                    reviews.append(text)
            except:
                continue

        if current_page == MAX_REVIEW_PAGES:
            break

        try:
            if current_page < 5:
                btn_index = 2 + current_page  # 페이지2: li[3], 3: li[4], ...
            else:
                btn_index = 6  # 6페이지 이상 고정

            # ✅ 실제 구조에 맞는 전체 XPath 사용
            next_button_xpath = f'/html/body/div[2]/div[2]/div[2]/div/div[2]/div[8]/nav/ul/li[{btn_index}]/button'
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, next_button_xpath))
            )
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
        except:
            print("❗ 다음 페이지 버튼 클릭 실패 또는 없음 → 종료")
            break

    return reviews

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
            print("✅ 영양성분 로딩 성공" if ingredient != '영양성분 없음' else "⚠️ 영양성분 없음")

            try:
                read_more = driver.find_element(By.XPATH, '//*[@id="product-reviews"]/ugc-pdp-review/ugc-apollo/div/div/div/div/div[2]/ugc-review-list/div/div[6]/ugc-read-more/a/span')
                driver.execute_script("arguments[0].click();", read_more)
                time.sleep(2)
            except:
                pass

            product_id = link.split("/")[-1]
            product_name = link.split("/")[-2]
            reviews = get_reviews(product_name, product_id)
            print(f"📝 수집된 리뷰 수: {len(reviews)}")

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
