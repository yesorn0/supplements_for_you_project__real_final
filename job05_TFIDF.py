import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.io import mmwrite

# 1. 리뷰 데이터 불러오기
df_review = pd.read_csv('./cleaned_data/cleaned_supplements.csv')

# 2. 결측치 제거 (리뷰, 제품명, 성분, URL 모두 있어야 함)
df_review = df_review[
    df_review['review'].notnull() &
    df_review['product'].notnull() &
    df_review['ingredient'].notnull() &
    df_review['url'].notnull()
]
df_review.to_csv('./cleaned_data/cleaned_supplements.csv', index=False)

# 3. 제품별로 리뷰 묶기
df_grouped_review = df_review.groupby('product')['review'].apply(lambda reviews: ' '.join(reviews)).reset_index()

# 4. 제품별 첫 번째 성분/URL 정보 가져오기
df_grouped_info = df_review.groupby('product')[['ingredient', 'url']].first().reset_index()

# 5. 병합
df_grouped = pd.merge(df_grouped_review, df_grouped_info, on='product')

print(df_grouped.info())
print(df_grouped.head())

# 6. TF-IDF 벡터화
tfidf = TfidfVectorizer(sublinear_tf=True)
tfidf_matrix = tfidf.fit_transform(df_grouped['review'])

print(tfidf_matrix.shape)
print(tfidf_matrix[0])

# 7. 모델 및 행렬 저장
with open('./models/tfidf.pickle', 'wb') as f:
    pickle.dump(tfidf, f)

mmwrite('./models/tfidf_supplements.mtx', tfidf_matrix)

# 8. 제품 정보 저장 (모두 포함)
df_grouped[['product', 'review', 'ingredient', 'url']].to_csv(
    './models/tfidf_products.csv', index=False, encoding='utf-8-sig'
)

print("✅ 제품 단위 TF-IDF 벡터화 및 저장 완료")
