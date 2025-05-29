import pandas as pd
from gensim.models import Word2Vec

# 1. 전처리된 리뷰 데이터 불러오기
df_review = pd.read_csv('./cleaned_data/cleaned_supplements.csv')
df_review = df_review[df_review['review'].notnull() & df_review['ingredient'].notnull()]  # 결측치 제거
print(df_review.info())

# 2. 리뷰 + 성분 병합 → 하나의 문장으로
df_review['combined'] = df_review['review'] + ' ' + df_review['ingredient']

# 3. 리스트로 추출
combined_texts = df_review['combined'].tolist()

# 4. 형태소 단위 분리 (띄어쓰기 기준)
tokens = []
for sentence in combined_texts:
    token = sentence.split()
    tokens.append(token)
print(tokens[:2])  # 확인용

# 5. Word2Vec 모델 학습
embedding_model = Word2Vec(
    sentences=tokens,
    vector_size=100,
    window=4,
    min_count=15,
    workers=4,
    epochs=100,
    sg=1  # Skip-gram
)

# 6. 모델 저장
embedding_model.save('./models/word2vec_supplements_combined.model')
print("✅ Word2Vec 모델 저장 완료")
print("단어 수:", len(embedding_model.wv.index_to_key))
