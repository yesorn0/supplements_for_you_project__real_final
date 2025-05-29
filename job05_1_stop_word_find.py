# 불용어 찾기
import pickle
import pandas as pd
import numpy as np

# 1. tfidf.pickle 파일 로드
with open('./models/tfidf.pickle', 'rb') as f:
    tfidf = pickle.load(f)

# 2. IDF 값과 단어 목록 추출
idf_values = tfidf.idf_
feature_names = tfidf.get_feature_names_out()

# 3. IDF 값의 범위 및 통계 출력
print(" IDF 최소값:", min(idf_values))
print(" IDF 최대값:", max(idf_values))
print(" 단어 수:", len(idf_values))

# 4. 가장 IDF 낮은 상위 10개 단어 출력
import pandas as pd

df_idf = pd.DataFrame({
    'word': feature_names,
    'idf': idf_values
})
print("\nIDF 가장 낮은 단어들:")
print(df_idf.sort_values(by='idf').head(10))


# 2. 단어(IDF 포함) 리스트 생성
idf_scores = tfidf.idf_  # IDF 점수 배열
feature_names = tfidf.get_feature_names_out()  # 각 단어 이름

# 3. DataFrame으로 정리
df_idf = pd.DataFrame({
    'word': feature_names,
    'idf': idf_scores
})

# 4. 낮은 IDF 기준으로 불용어 후보 추출 (자주 등장하는 단어)
idf_threshold = 1.5  # 너무 흔한 단어 기준값 (조절 가능)
stopword_candidates = df_idf[df_idf['idf'] < idf_threshold].sort_values(by='idf')

# 5. 결과 출력
print("자주 등장하는 불용어 후보 단어 (IDF < 1.5):")
print(stopword_candidates.head(30))  # 상위 30개만 보기

# 6. CSV 저장 (선택)
stopword_candidates.to_csv('./models/auto_stopwords_candidates.csv', index=False, encoding='utf-8-sig')




