import pandas as pd
from gensim.models import Word2Vec
from konlpy.tag import Okt
import os
import re

# 1. 데이터 불러오기
df = pd.read_csv('./cleaned_data/cleaned_supplements.csv')

# 2. 결측치 제거
df = df[df['review'].notnull() & df['product'].notnull()]
df = df[(df['review'].str.strip() != '') & (df['product'].str.strip() != '')]

# 3. 리뷰 + 제품을 결합
df['combined'] = df['review'] + ' ' + df['product']

# 4. 형태소 분석기 준비
okt = Okt()

# 5. 정제 + 토큰화
def clean_and_tokenize(text):
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)  # 특수문자 제거
    return okt.nouns(text)

tokens = [clean_and_tokenize(sentence) for sentence in df['combined'].tolist()]

# 6. Word2Vec 모델 학습
embedding_model = Word2Vec(
    sentences=tokens,
    vector_size=150,
    window=15,
    min_count=5,
    workers=4,
    epochs=100,
    sg=1  # Skip-gram 방식
)

# 7. 저장 디렉토리 생성
os.makedirs('./models', exist_ok=True)

# 8. 모델 저장
embedding_model.save('./models/word2vec_supplements_okt.model')

# 9. 요약 출력
print("✅ Word2Vec 모델 저장 완료")
print(f"단어 수: {len(embedding_model.wv.index_to_key)}개")
print("예시 단어:", embedding_model.wv.index_to_key[:10])
