import pandas as pd
import time
import pickle
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ 크롬 드라이버 설정
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

# ✅ 쿠키 설정
cookie_path = "cookies.pkl"
def load_cookies():
    if os.path.exists(cookie_path):
        driver.get("https://kr.iherb.com")
        with open(cookie_path, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    continue
        driver.refresh()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

def save_cookies():
    with open(cookie_path, "wb") as f:
        pickle.dump(driver.get_cookies(), f)

if not os.path.exists(cookie_path):
    print("❗ CAPTCHA 수동 인증 필요 → 완료 후 Enter")
    driver.get("https://kr.iherb.com")
    input("👉 Enter를 눌러 계속하세요...")
    save_cookies()
else:
    load_cookies()

# ✅ 카테고리 URL
categories = {
    '비타민 B': 'https://kr.iherb.com/c/vitamin-b?_gl=1*bdnx4f*_up*MQ..*_gs*MQ..&gclid=Cj0KCQjwxdXBBhDEARIsAAUkP6h0GZY2d4NZTb_1rrBwm_uJgngZPJwHMr5SBPnCQ6ZxJ7Mo8txjZZsaAh4eEALw_wcB&gclsrc=aw.ds&sr=2',
    '비타민 A': 'https://kr.iherb.com/c/vitamin-a?_gl=1*rjalno*_up*MQ..*_gs*MQ..&gclid=Cj0KCQjwxdXBBhDEARIsAAUkP6h0GZY2d4NZTb_1rrBwm_uJgngZPJwHMr5SBPnCQ6ZxJ7Mo8txjZZsaAh4eEALw_wcB&gclsrc=aw.ds&sr=2'
}

# ✅ 파일 경로
file_paths = {
    '비타민 A': './crawling_data/iherb_uc_비타민 A_update.csv',
    '비타민 B': './crawling_data/iherb_uc_비타민 B_update.csv'
}

# ✅ 제품 정보 추출 함수
def extract_info(url):
    try:
        driver.get(url)
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        product = driver.find_element(By.XPATH, '//*[@id="name"]').text.strip()
        try:
            table = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[8]/article/div[2]/div/section/div[2]/div/div[1]/div[2]/div/table/tbody'))
            )
            ingredient = table.text.strip()
        except:
            ingredient = '영양성분 없음'
        return product, ingredient, url
    except Exception as e:
        return '오류', '오류', url

# ✅ 제품 링크 수집
def get_product_links():
    links = []
    for i in range(1, 100):  # 최대 100개 시도
        try:
            xpath = f'/html/body/div[7]/div/div[3]/div/div/div[1]/div[1]/div[3]/div[{i}]/div/div[2]/div[1]/a'
            element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, xpath)))
            href = element.get_attribute('href')
            if href:
                links.append(href)
        except:
            continue
    return links

# ✅ 메인 실행
for category, url in categories.items():
    print(f"\n📦 {category} 카테고리 처리 시작...")
    df = pd.read_csv(file_paths[category])
    df['product'] = df['product'].astype(str).str.strip()
    target_names = set(df['product'])
    found = []

    driver.get(url)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    product_links = get_product_links()

    for link in product_links:
        product, ingredient, page_url = extract_info(link)
        if product in target_names:
            print(f"✅ 일치: {product}")
            found.append({'product': product, 'ingredient': ingredient, 'url': page_url})
        else:
            print(f"❌ 불일치: {product}")
        if len(found) >= len(target_names):
            break
        time.sleep(1.5)

    # ✅ 병합을 위한 처리
    found_df = pd.DataFrame(found)
    if 'url' not in found_df.columns:
        found_df['url'] = ''
    if 'ingredient' not in found_df.columns:
        found_df['ingredient'] = ''
    found_df['product'] = found_df['product'].astype(str).str.strip()

    # ✅ 순서 유지 병합
    merged_df = df.merge(found_df, on='product', how='left', suffixes=('', '_new'))
    for col in ['ingredient', 'url']:
        if f"{col}_new" in merged_df.columns:
            merged_df[col] = merged_df[f"{col}_new"].combine_first(merged_df[col])
            merged_df.drop(columns=[f"{col}_new"], inplace=True)

    # ✅ 저장
    output_path = file_paths[category].replace(".csv", "_filled.csv")
    merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"📁 저장 완료 → {output_path}")

# ✅ 종료
driver.quit()
print("\n🎉 모든 카테고리 크롤링 완료!")
