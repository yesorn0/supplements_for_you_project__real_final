import pandas as pd

# 기존 CSV와 보완 CSV 로드
df_original = pd.read_csv('./crawling_data/iherb_uc_비타민 B.csv')
df_missing = pd.read_csv('./crawling_data/비타민B_합친리뷰.csv')

# 두 데이터프레임 합치기
df_combined = pd.concat([df_original, df_missing], ignore_index=True)

# 중복 제거: review 조합이 동일한 경우만 제거
df_combined.drop_duplicates(subset=['review'], inplace=True)

# 저장
df_combined.to_csv('combined.csv', index=False, encoding='utf-8-sig')
