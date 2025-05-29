import pandas as pd
from gensim.models import Word2Vec
import os

# 1. 전처리된 리뷰 데이터 불러오기
df_review = pd.read_csv('./cleaned_data/cleaned_supplements.csv')
df_review = df_review[df_review['review'].notnull()]  # 결측치 제거
print(df_review.info())

# 2. 리뷰 리스트 추출
reviews = df_review['review'].tolist()

# 3. 형태소 단위 분리 (띄어쓰기 기준)
tokens = []
for sentence in reviews:
    token = sentence.split()  # 전처리 시 형태소 분석 완료된 문장
    tokens.append(token)
print(tokens[:2])  # 확인용

# 4. Word2Vec 모델 학습
embedding_model = Word2Vec(
    sentences=tokens,
    vector_size=100,
    window=4,
    min_count=15,
    workers=4,
    epochs=100,
    sg=1  # Skip-gram
)

# 5. 모델 저장
embedding_model.save('./models/word2vec_supplements_review.model')
print("✅ Word2Vec 모델 저장 완료")
print("단어 수:", len(embedding_model.wv.index_to_key))
