# # 이제부터는 각자 작업
# import pandas as pd
# import glob
#
# # data_paths = glob.glob('./crawling_data/*')
# data_paths = glob.glob('./preprocessed_data/*')
# print(data_paths)
#
# # 빈 데이터 프레임 만들기
# df = pd.DataFrame()
#
# for path in data_paths:
#     df_temp = pd.read_csv(path)
#     df_temp.columns = ['titles', 'reviews']
#     df_temp.dropna(inplace=True)
#     df = pd.concat([df, df_temp], ignore_index= True)
# df.drop_duplicates(inplace=True) # 중복제거
# df.info()
# print(df.head())
# #cleaned_data 폴더 안에 movie_reviews.csv파일 저장
# df.to_csv('./cleaned_data/movie_reviews.csv', index=False)
#
#
# # --------------------------------------------------------------------------------
# # glob 모듈을 이용해 movie_reviews 폴더 안의 모든 파일 경로를 가져옴(리스트 형태로 저장)
# data_paths = glob.glob('./cleaned_data/*')
# # 최종적으로 모든 데이터를 저장할 빈 DataFrame 생성
# df = pd.DataFrame()
#
# # 위에서 불러온 각 csv파일 경로마다 반복 수행
# for path in data_paths:
#     # 현재 경로(path)의 csv파일을 불러와 임시 데이터프레임(df_temp)에 저장
#     df_temp = pd.read_csv(path)
#     # 컬럼을 0번, titles, 1번, reviews로 변경
#     df_temp.columns = ['titles', 'reviews']
#     titles = []
#     reviews =[]
#     old_title = ''
#     for i in range(len(df_temp)):
#         title = df_temp.iloc[i, 0]
#         if title != old_title: # 중복된 제목을 한번만 추가하게 csv를 보면 제목이 모두 달려있어서 그럼
#             titles.append(title)
#             old_title = title
#             df_movie = df_temp[(df_temp.titles == title)]
#             review = ' '.join(df_movie.reviews) # 띄어쓰기 기준으로 모두 하나로 합침?
#             reviews.append(review)
#     print(len(titles))
#     print(len(reviews))
#     df_batch = pd.DataFrame({'titles':titles, 'reviews':reviews})
#     df = pd.concat([df, df_batch], ignore_index= True)
# df.drop_duplicates(inplace=True) # 중복제거
# df.info()
# df.to_csv('./cleaned_data/movie_reviews.csv', index=False)


import pandas as pd # pandas : 테이블형태의 데이터를 다루기 위한 라이브러리
import glob # 폴더 안에 있는 파일들을 한번에 불러 올 수 있게 해주는 도구

# 여러개의 파일에서 데이터를 읽고 하나로 모은 다음 저장하는 단계

# 폴더 안에 있는 모든 파일의 경로를 리스트로 저장
data_paths = glob.glob('./preprocessed_data/*')
print(data_paths) # 파일 경로가 제대로 모였는지 확인(중간 확인용)
df = pd.DataFrame() # 통합 데이터를 담을 빈 데이터프레임(df) 생성

# 파일 하나씩 반복해서 읽기
for path in data_paths: # 파일 하니씩 반복해서 읽기
    df_temp = pd.read_csv(path) # 현재 파일을 읽어와 임시로 저장
    df_temp.columns = ['titles', 'reviews'] # 컬럼 이름을 titles, reviews로 바꾸기
    df_temp.dropna(inplace=True)  #결측값(NaN, 비어있는 값)이 있는 행은 제거
    df = pd.concat([df, df_temp], ignore_index=True) # 기존의 df에 에 이 데이터를 합친다. index는 무시하고 새로 부여
df.drop_duplicates(inplace=True) # 중복된 행을제거(같은제목 + 리뷰가 완전히 같은 경우)
df.info() # 데이터 개요를 확인 (총 행수, 각 컬럼 타입 등)
print(df.head())
# 정리된 데이터를 cleaned_data 폴더에 movie_reviews.csv로 저장
df.to_csv('./cleaned_data/movie_reviews.csv', index=False)

# ------------------------------------------------------------------------

# 저장된 movie_reviews.csv 파일을 다시 읽어 같은 영화 제목끼리 리뷰를 합치는 작업
data_paths = glob.glob('./cleaned_data/*') # cleaned_data 폴더 안의 모든 파일을 불러옴
df = pd.DataFrame() # 새로 데이터를 담을 빈 프레임 생성

for path in data_paths: # 폴더 안의 각 파일마다 반복
    df_temp = pd.read_csv(path) # 파일 읽기
    df_temp.columns = ['titles', 'reviews'] # 컬럼 이름을 'titles', 'reviews' 로 맞춤
    # 같은 제목을 가진 리뷰들을 합치기 위해 변수 초기화
    titles = [] # 고유한 영화 제목만 저장
    reviews = [] # 해당 제목의 모든 리뷰를 합친 결과 저장
    old_title = '' # 이전에 저장한 제목을 기억해두기 위한 변수

    # 데이터 프레임을 한 줄씩 읽기
    for i in range(len(df_temp)):
        title = df_temp.iloc[i, 0]

        # 현재 제목이 이전 제목과 다르면(즉 새로운 영화면)
        if title != old_title:
            titles.append(title)    # 새 제목을 리스트에 추가
            old_title = title       # 현재 제목을 old_title로 저장

            # 이 제목을 가진 모든 리뷰를 모아서 하나의 문자열로 저장
            df_movie = df_temp[df_temp.titles == title]
            review = ' '.join(df_movie.reviews) # 공백을 기준으로 리뷰들을 구분하기
            reviews.append(review) # 리뷰를 리스트에 추가


    print(len(titles))
    print(len(reviews))
    df_batch = pd.DataFrame({'titles':titles, 'reviews':reviews})    # titles, reviews 리스트를 데이터프레임으로 만들기
    df = pd.concat([df, df_batch], ignore_index=True)           # 기존 df에 이 결과를 합치기


df.info() # 전체 데이터 구조 확인
df.to_csv('./cleaned_data/movie_reviews.csv', index=False) # 최종 데이터 저장