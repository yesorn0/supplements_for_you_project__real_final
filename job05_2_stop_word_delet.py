import pandas as pd

# 파일 경로
stopwords_path = "./models/auto_stopwords_candidates.csv"

# 유지할 단어들
keywords_to_keep = set([
    '증가', '감소', '이점', '건강 보조', '균형', '여성', '작용', '비타민 섭취', '긍정', '효과 느끼다',
    '건강 유지', '스트레스', '종합 비타민', '성분 구성', '항산화제', '수면', '손톱', '오메가', '영향 미치다',
    '연령', '증지', '심장', '향상 시키다', '머리카락', '항산화', '강화하다', '아연', '혈액', '촉진', '대사',
    '최적', '성분 효능', '비타민 성분', '임신', '건강 개선', '칼슘', '신경계', '근육', '면역체게', '염증',
    '비타민 보충', '어린이', '결핍 보충', '품질 비타민', '호르몬', '필수 영양소', '혈관', '비타민 비타민',
    '엽산', '관절', '효과',
])

# 데이터 불러오기
df_stop = pd.read_csv(stopwords_path)

# 제거할 불용어만 추출
df_stop_filtered = df_stop[~df_stop['word'].isin(keywords_to_keep)].copy()

# 파일로 저장
filtered_path = "./models/filtered_stopwords.csv"
df_stop_filtered.to_csv(filtered_path, index=False, encoding="utf-8-sig")
