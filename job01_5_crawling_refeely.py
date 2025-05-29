import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import pickle
import os
import time

MAX_PRODUCTS = 48
RETRY_COUNT = 3

# categories = {
#     '비타민 E': 'https://kr.iherb.com/c/vitamin-e?_gl=1*q03ogu*_up*MQ..*_gs*MQ..&gclid=Cj0KCQjwxdXBBhDEARIsAAUkP6h0GZY2d4NZTb_1rrBwm_uJgngZPJwHMr5SBPnCQ6ZxJ7Mo8txjZZsaAh4eEALw_wcB&gclsrc=aw.ds&sr=2',
#     '비타민 D': 'https://kr.iherb.com/c/vitamin-d?_gl=1*1ypxyyf*_up*MQ..*_gs*MQ..&gclid=Cj0KCQjwxdXBBhDEARIsAAUkP6h0GZY2d4NZTb_1rrBwm_uJgngZPJwHMr5SBPnCQ6ZxJ7Mo8txjZZsaAh4eEALw_wcB&gclsrc=aw.ds&sr=2',
#     '비타민 C': 'https://kr.iherb.com/c/vitamin-c?_gl=1*bdnx4f*_up*MQ..*_gs*MQ..&gclid=Cj0KCQjwxdXBBhDEARIsAAUkP6h0GZY2d4NZTb_1rrBwm_uJgngZPJwHMr5SBPnCQ6ZxJ7Mo8txjZZsaAh4eEALw_wcB&gclsrc=aw.ds&sr=2'
#     '비타민 B': 'https://kr.iherb.com/c/vitamin-b?_gl=1*bdnx4f*_up*MQ..*_gs*MQ..&gclid=Cj0KCQjwxdXBBhDEARIsAAUkP6h0GZY2d4NZTb_1rrBwm_uJgngZPJwHMr5SBPnCQ6ZxJ7Mo8txjZZsaAh4eEALw_wcB&gclsrc=aw.ds&sr=2',
#     '비타민 A': 'https://kr.iherb.com/c/vitamin-a?_gl=1*rjalno*_up*MQ..*_gs*MQ..&gclid=Cj0KCQjwxdXBBhDEARIsAAUkP6h0GZY2d4NZTb_1rrBwm_uJgngZPJwHMr5SBPnCQ6ZxJ7Mo8txjZZsaAh4eEALw_wcB&gclsrc=aw.ds&sr=2'
# }

# categories = {
#     '칼슘': 'https://kr.iherb.com/c/calcium?sr=2',
#     '콜린': 'https://kr.iherb.com/c/choline?sr=2',
#     '요오드': 'https://kr.iherb.com/c/iodine?sr=2',
#     '철분': 'https://kr.iherb.com/c/iron?sr=2',
#     '마그네슘': 'https://kr.iherb.com/c/magnesium?sr=2'
# }

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

def get_product_name_with_retry(retry=RETRY_COUNT):
    for attempt in range(1, retry + 1):
        try:
            element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="name"]'))
            )
            return element.text.strip()
        except:
            print(f"⏳ 제품명 로딩 재시도 ({attempt}/{retry})")
            time.sleep(1 + attempt)  # 재시도마다 대기 시간 증가
    return '제품명 없음'

def get_ingredient_with_retry(retry=RETRY_COUNT):
    for attempt in range(1, retry + 1):
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="product-overview"]/div/section/div[2]/div/div[1]/div[2]/div/table/tbody'))
            )
            return element.text.strip()
        except:
            print(f"⏳ 영양성분 로딩 재시도 ({attempt}/{retry})")
            time.sleep(1 + attempt)
    return '영양성분 없음'

def merge_ingredient_and_url(df_old, df_new):
    for col in ['ingredient', 'url']:
        if col not in df_old.columns:
            df_old[col] = pd.NA

    df_merged = df_old.merge(
        df_new[['product', 'ingredient', 'url']], on='product', how='left', suffixes=('', '_new')
    )

    for col in ['ingredient', 'url']:
        new_col = f"{col}_new"
        if new_col in df_merged.columns:
            df_merged[col] = df_merged[col].combine_first(df_merged[new_col])
            df_merged.drop(columns=[new_col], inplace=True)
        else:
            print(f"⚠️ 병합할 {new_col} 없음")

    return df_merged

# ✅ 크롤링 및 병합 루프
for supplement, url in categories.items():
    print(f"\n📦 '{supplement}' 카테고리 수집 시작...")
    data = []

    driver.get(url)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    product_links = get_product_links()
    print(f"🔗 수집된 링크 수: {len(product_links)}")

    for idx, link in enumerate(product_links):
        print(f"➡️ [{idx+1}/{len(product_links)}] 제품 크롤링 중: {link}")
        try:
            driver.get(link)
            time.sleep(2)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            product = get_product_name_with_retry()
            print(f"📌 제품명: {product}" if product != '제품명 없음' else f"⚠️ 제품명 로딩 실패 → {link}")

            ingredient = get_ingredient_with_retry()
            print("✅ 영양성분 수집 완료" if ingredient != '영양성분 없음' else "⚠️ 영양성분 없음")

            data.append({
                'supplements': supplement,
                'product': product,
                'ingredient': ingredient,
                'url': link
            })

        except Exception as e:
            print(f"[❌ 오류 발생] {link} - {e}")
            continue

    df_new = pd.DataFrame(data)
    existing_path = f"iherb_uc_{supplement}.csv"
    if os.path.exists(existing_path):
        df_old = pd.read_csv(existing_path)
        print(f"📂 기존 파일 로드 완료: {existing_path}")
        df_merged = merge_ingredient_and_url(df_old, df_new)
        output_path = f"iherb_uc_{supplement}_updated.csv"
        df_merged.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✅ 병합 및 저장 완료 → {output_path}")
    else:
        df_new.to_csv(f"iherb_uc_{supplement}_new.csv", index=False, encoding='utf-8-sig')
        print(f"⚠️ 기존 파일 없음 → 신규 저장 완료")

driver.quit()
print("🔚 전체 크롤링 및 병합 완료")
