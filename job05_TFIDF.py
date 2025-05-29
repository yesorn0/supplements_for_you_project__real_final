import pickle  # 모델 저장용
import pandas as pd  # 데이터프레임 처리
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.io import mmwrite  # 희소 행렬 저장

# 1. 리뷰 데이터 불러오기
df_review = pd.read_csv('./cleaned_data/cleaned_supplements.csv')

# 2. 결측치 제거 (리뷰 및 제품명이 모두 있어야 함)
df_review = df_review[df_review['review'].notnull() & df_review['product'].notnull()]
df_review.to_csv('./cleaned_data/cleaned_supplements.csv', index=False)

# 3. 제품별로 리뷰 묶기 (한 제품에 여러 리뷰가 있는 경우)
df_grouped = df_review.groupby('product')['review'].apply(lambda reviews: ' '.join(reviews)).reset_index()

print(df_grouped.info())
print(df_grouped.head())

# 4. TF-IDF 벡터화기 정의
tfidf = TfidfVectorizer(sublinear_tf=True)  # 로그 스케일 적용

# 5. TF-IDF 행렬 생성 (제품별 문서)
tfidf_matrix = tfidf.fit_transform(df_grouped['review'])

print(tfidf_matrix.shape)  # (제품 수, 단어 수)
print(tfidf_matrix[0])     # 첫 번째 제품의 TF-IDF 벡터 출력

# 6. 모델 및 행렬 저장
with open('./models/tfidf.pickle', 'wb') as f:
    pickle.dump(tfidf, f)

mmwrite('./models/tfidf_supplements.mtx', tfidf_matrix)

# 7. 제품 이름 리스트도 따로 저장 (추천 결과와 매핑할 수 있도록)
df_grouped[['product']].to_csv('./models/tfidf_products.csv', index=False, encoding='utf-8-sig')

print("✅ 제품 단위 TF-IDF 벡터화 및 저장 완료")
