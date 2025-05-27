# TFIDF, DTM 내에 있는 각 단어에 대한 중요도를 계산할 수 있는 TF-IDF 가중치
import pickle # TF-IDF와 벡터결과를 저장하기 위한 pickle 모듈
import pandas as pd # CSV파일을 읽고 다루기 위해 사용하는 데이터프레임 라이브러리
from sklearn.feature_extraction.text import TfidfVectorizer # 텍스트를 숫자로 변환해주는 도구 (TI-IDF 방식)
from scipy.io import mmwrite # 희소행렬(sparese matrix)을 .mtx 포멧으로 저장하는 함수

# 정제된 리뷰 데이터 불러오기 및 전처리
df_review = pd.read_csv('./cleaned_data/cleaned_reviews.csv') # 정제된 리뷰 csv파일을 읽어서 데이터 프레임으로 저장
df_review.dropna(inplace=True) # 혹시 모를 빈 값(Nan)이 있다면 제거
df_review.to_csv('./cleaned_data/cleaned_reviews.csv', index = False) # 다시저장, 깨끗한 파일로 덮어쓰기
df_review.info() # 데이터프레임 구조 확인(행, 컬럼, 타입 등)

# ------------------------------------------------------------------------------------------
# TF-IDF 벡터화 진행

# sublinear_tf=True는 로그 스케일 적용 → 너무 자주 나오는 단어의 가중치를 낮춤
tfidf = TfidfVectorizer(sublinear_tf=True) # TF-IDF벡터화기(TfidfVectorizer) 생성

# 각 리뷰를 벡터로 바꿔서 tfidf_matrix에 저장(희소행렬 형태)
tfidf_matrix = tfidf.fit_transform(df_review['reviews']) # 'reviews' 컬럼의 텍스트 데이터를 벡터화하여 숫자로 변환
print(tfidf_matrix.shape) # 생성된 행렬의 크기를 확인
print(tfidf_matrix[0]) # 첫번째 리뷰의 벡터값 출력(희소 행렬 구조로 출력됨)

#------------------------------------------------------------------------------------------
# 모델과 데이터 저장

#TF-IDF 벡터화기를 피클 파일로 저장(나중에 예측할 때 다시 사용하기 위함)
with open('./models/tfidf.pickle', 'wb') as f: # 'wb' write binary모드(바이너리 파일 저장)
    pickle.dump(tfidf, f)

# 희소행렬(tfidf_matrix)을 .mtx 형태로 저장(메모리 효율적으로 저장 가능)
mmwrite('./models/tfidf_movie_review.mtx', tfidf_matrix)


