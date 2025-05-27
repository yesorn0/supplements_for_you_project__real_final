import pandas as pd # 데이터 처리/분석을 위한 라이브러리
from gensim.models import Word2Vec  # gensim은 자연어처리용 라이브러리, Word2Vec은 단어 벡터 생성기

df_review = pd.read_csv('./cleaned_data/cleaned_reviews.csv')
df_review.info()

reviews = list(df_review['reviews']) # df_review에서 reviews열(컬럼)만 가져옴
# 자연어 처리가 끝난(전처리가 다 된) 형태의 문장이 출력됨
print(df_review.iloc[0, 0], reviews[0]) # 첫번째 리뷰를 두가지 방식으로 출력
# .lioc[0, 0] : 첫번째 행의 첫번째 열을 가져옴
# reviews[0] : 리스트에서 첫 번째 요소를 꺼낸다.
# 둘다 같은 데이터를 출력하게 될것, 전처리된 문장인지 확인하는 용도

# 형태소 단위로 잘라서 list로 볼것
tokens = [] # 형태소 분리된 리뷰 문장을 저장할 빈 리스트 생성
for sentence in reviews:
    # token은 형태소들의 리스트
    token = sentence.split() # 공백 기준으로 문자열을 나눠서 단이 리스트로 만듬
    tokens.append(token) # 만든 단어 리스트를 tokens 리스트에 추가
print(tokens[0:2]) # 처음 두 개의 문장이 어떻게 분리되었는지 확인

# ------------------------------------------------------------------------
# Word2Vec 모델 학습
embedding_model = Word2Vec(tokens, vector_size= 100, window=4,
                           min_count=15, workers=4, epochs=100, sg=1)
# tokens : 학습에 사용할 문장리스트, # vector_size = 100 : 각 단어를 100차원 벡터로 표현
# window = 4 : 한 단어 주변 최대 4개의 단어까지 문맥으로 사용, # min_count = 15 : 15번 미난 등장한 단어는 무시 -> 희귀 단어 제거
# workers = 4 : 병렬처리를 위해 CPU 코어 4개 사용, # epochs = 100 : 전체데이터를 100번 반복학습
# sg =1 : Skip = Gram 방식 사용(문맥으로 주변 단어 예측), # sg = 0 이면 CBOW방식(반대구조)

embedding_model.save('./models/word2vec_movie_review.model') # 학습한 모델 저장
print(list(embedding_model.wv.index_to_key)) # 학습된 단어 리스트 출력
print(len(embedding_model.wv.index_to_key)) # 학습된 단어의 총 개수를 출력