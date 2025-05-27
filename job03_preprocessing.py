import pandas as pd
import re # 정규표현식, 텍스트에서 특정패턴(한글, 숫자 등)을 걸러낼 때 사용
# 형태소 분석기, 한국어 문장을 단어 단위로 분석하여 품사 정보를 붙여줌
from konlpy.tag import Okt # 처음 사용하는거면 자바 설치해야함  

# 정제된 CSV 파일 불러오기
df = pd.read_csv('./cleaned_data/movie_reviews.csv')
df.info()   # 데이터 개요 확인(행수, 컬럼 명, 결측치 등)
print(df.head())    # 실제 데이터 일부 보기

# 의미없는 단어(불용어) 제거
stop_words = ['영화', '감독', '연출', '배우', '하다', '있다', '없다', '보다'
    , '되다','연기', '작품', '이다', '내다', '아니다', '크다']

# 형태소 분석 준비
okt = Okt() # Okt 객체 생성(형태소 분석기)
cleaned_sentences = []  # 정제된 문장들을 저장할 리스트

# 리뷰 하나씩 반복해서 처리, # 명사, 동사, 부사 와 같이 영화와 관련된 단어들을 가져가야 한다
for review in df.reviews:
    review = re.sub('[^가-힣]', ' ', review) # 한글(가-힣)제외 모두 제거(영어, 숫자, 기호 등 제거)
    # pos와 mos 차이점 알아보기
    tokend_review = okt.pos(review, stem=True) # 형태소 분석 수행, 원형 복원(stem = True)
    # print(tokend_review)
    # 분석결과를 데이터프레임으로 바꿔서 보기좋게 정리 #조금 더 디테일하게 전처리 진행
    df_token = pd.DataFrame(tokend_review, columns=['word', 'class'])
    # print(df_token)
    
    #명사, 형용사, 동사만 남김(이 외 감탄사, 조사, 구두점 등 제거)
    df_token = df_token[(df_token['class']=='Noun') |
                        (df_token['class'] == 'Adjective') |
                        (df_token['class'] == 'Verb')]

    # print(df_token)
    # 단어 길이 1글자 이하 제거
    words = [] # 필터링된 단어를 저장
    for word in df_token.word:
        if 1 < len(word):   # 글자 수가 2이상인 단어만 사용
            if word not in stop_words:
                words.append(word)
    cleaned_sentence = ' '.join(words)  # 단어들을 공백으로 연결하여 문장 형태로 만듬
    print(cleaned_sentence)             # 중간확인(정제된 문장)
    cleaned_sentences.append(cleaned_sentence)  # 최종 문장 리스트에 추가

# DataFrame에 적용 및 저장
df['reviews'] = cleaned_sentences # 정제된 문장으로 기존 리뷰 데이터 대체
df.dropna(inplace= True)            # 결측값 제거
df.drop_duplicates(inplace=True)    # 중복 제거
df.info()                           # 정보 확인
print(df.head())                    # 일부 데이터 확인
df.to_csv('./cleaned_data/cleaned_reviews.csv', index= False) # 최종 정제된 리뷰를 다시 CSV로 저장

# 한번 더 점검, # 혹시 모를 결측치 확인 및 재저장(안전한 후 처리)
df = pd.read_csv('./cleaned_data/cleaned_reviews.csv')
df.dropna(inplace=True)
df.info()
df.to_csv('./cleaned_data/cleaned_reviews.csv', index = False)

