import pandas as pd
import glob

# 1. crawling_data 폴더 내 모든 CSV 파일 불러오기
data_paths = glob.glob('./crawling_data/*.csv')
df = pd.DataFrame()

for path in data_paths:
    df_temp = pd.read_csv(path)
    df_temp.columns = ['supplements', 'product', 'ingredient', 'review', 'url']
    df = pd.concat([df, df_temp], ignore_index=True)

# 1. 공백 제거 및 대문자 처리
df['supplements'] = df['supplements'].str.replace(" ", "").str.upper()

# 2. 표준화 (띄어쓰기 포함해서 복원)
df['supplements'] = df['supplements'].replace({
    '비타민A': '비타민 A',
    '비타민B': '비타민 B',
    '비타민C': '비타민 C',
    '비타민D': '비타민 D',
    '비타민E': '비타민 E',
    '남성용비타민': '남성 종합비타민',
    '남성종합비타민': '남성 종합비타민',
    '여성종합비타민': '여성 종합비타민',
    '임산부종합비타민': '임산부 종합비타민',
})

# 3. 리뷰 중복 제거 + NaN 제거
# df.drop_duplicates(subset=['review'], inplace=True)
df.dropna(inplace=True)

# 4. 저장
df.to_csv('./cleaned_data/supplements.csv', index=False, encoding='utf-8-sig')
print("✅ 통합 및 저장 완료")

# 5. 비타민 종류별 개수 확인
supplement_counts = df['supplements'].value_counts()
print("💊 비타민 종류별 제품 수:")
print(supplement_counts)

# 6. 총 리뷰 수
valid_reviews = df['review'].dropna()
valid_reviews = valid_reviews[valid_reviews.str.strip() != '']
print(f"📝 총 리뷰 개수: {len(valid_reviews)}개")
