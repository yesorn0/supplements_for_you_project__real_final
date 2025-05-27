from itertools import count

import pandas as pd # 데이터프레임 처리용(csv읽기, 필터링용)
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity # 코사인 유사도 계산용
from scipy.io import mmread # .mtx 파일을 읽어들이는 함수
import pickle # TF-IDF 벡터 변환기를 불러오기 위한 모듈

# ------------------------------------------------------------------------------------

# 추천함수 정의
# 유사도 행렬을 받아서 유사한 영화 10개를 반환하는 함수
def getRecommendation(cosine_sim):
    simScore = list(enumerate(cosine_sim[-1])) # 각 영화의 유사도 점수를 인데그와 함께 리스트로 저장
    simScore = sorted(simScore, key = lambda x:x[1], reverse=True) # 유사도가 높은 순으로 정렬
    simScore = simScore[:11] # 자기 자신 + 유사한 영화 10개 선택
    movie_idx = [i[0] for i in simScore] # 인덱스만 따로 추출
    rec_movie_list = df_reviews.iloc[movie_idx, 0] # 제목 컬럼(index 0)을 기반으로 추천 목록 생성
    return rec_movie_list[1:11] # 자기 자신은 제외하고 10개만 반환

# ------------------------------------------------------------------------------------

# 리뷰데이터 불러오기
df_reviews = pd.read_csv('./cleaned_data/cleaned_reviews.csv') # 정제된 데이터 불러오기
# df_reviews.dropna(inplace= True)
df_reviews.info() # 데이터 구조 확인
print(str(df_reviews.iloc[1126, 1])) # 1126번째 리뷰 출력 -> 추천이 어떻게 동작하는지 확인용

# TF-IDF벡터 불러오기
tfidf_matrix = mmread('./models/tfidf_movie_review.mtx').tocsr() #.mtx 형식의 희소행렬 파일을 불러온 뒤, csr형식(빠른 행 연산진원)으로 변환
with open('./models/tfidf.pickle', 'rb') as f : # pickle 파일에서 TF-IDF 변환기 객체 불러오기
    tfidf = pickle.load(f)

# ------------------------------------------------------------------------------------


## 영화 index를 이용한 추천
# 추천대상 문장 선택
# ref_idx = 100 # 추천기준이 될 영화 인덱스(50번째 영화)
# print(df_reviews.iloc[ref_idx, 0]) # 기준영화 제목 출력
#
# # ------------------------------------------------------------------------------------
# # 기준영화(50번)과 모든 영화 사이의 유사도 계산(linear_kernel은 cosine similarity와 동일효과)
# cosine_sim = linear_kernel(tfidf_matrix[ref_idx], tfidf_matrix)
#
# print(cosine_sim) # 유사도 점수(0~1 사이) 출력
# print(len(cosine_sim[0])) # 코사인값이 1163개 있다.
# # ------------------------------------------------------------------------------------
# # 추천 목록 생성
# recommendation = getRecommendation(cosine_sim) # 추천 결과 받아오기
# print(recommendation[1:]) # 추천된 영화 제목 출력

# ------------------------------------------------------------------------------------
## Keyword를 이용한 추천
embedding_model = Word2Vec.load('./models/word2vec_movie_review.model')
keyword = '여름'
sim_word = embedding_model.wv.most_similar(keyword, topn= 10)
words = [keyword]
for word, _ in sim_word :
    words.append(word)
sentence = []
count = 10

for word in words :
    sentence = sentence + [word] * count
    count -= 1
sentence = ' '.join((sentence))
print(sentence)


sentence_vec = tfidf.transform([sentence])
cosine_sim = linear_kernel(sentence_vec, tfidf_matrix)
recommendation = getRecommendation(cosine_sim)
print(recommendation)
