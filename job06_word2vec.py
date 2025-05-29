import pandas as pd
from gensim.models import Word2Vec
import os

# 1. 데이터 불러오기
df = pd.read_csv('./cleaned_data/cleaned_supplements.csv')


# 2. 결측치 제거
df = df[df['review'].notnull() & df['ingredient'].notnull()]
df = df[(df['review'].str.strip() != '') & (df['ingredient'].str.strip() != '')]


# 3. 리뷰 + 성분을 하나로 결합
df['combined'] = df['review'] + ' ' + df['ingredient']

# 4. 문장을 띄어쓰기 기준으로 토큰화
tokens = [sentence.split() for sentence in df['combined'].tolist()]

# 5. Word2Vec 모델 학습
embedding_model = Word2Vec(
    sentences=tokens,
    vector_size=100,
    window=4,
    min_count=15,
    workers=4,
    epochs=100,
    sg=1  # Skip-gram 방식
)

# 6. 저장 디렉토리 생성
os.makedirs('./models', exist_ok=True)

# 7. 모델 저장
embedding_model.save('./models/word2vec_supplements_combined.model')

# 8. 학습 결과 요약 출력
print("✅ Word2Vec 모델 저장 완료")
print(f"단어 수: {len(embedding_model.wv.index_to_key)}개")
print("예시 단어:", embedding_model.wv.index_to_key[:10])
