# 문자열 데이터 시각화 # wordcloud를 통해 어떤 단어들이 많이 나오는지 확인, 시각화
import collections # 단어 빈도를 셀 수 있는 collections 모듈
import pandas as pd # 데이터프레임을 다루기 위한 pandas
from mpl_toolkits.mplot3d.proj3d import world_transformation
from wordcloud import WordCloud # 워드 클라우드 생성 라이브러리
import matplotlib.pyplot as plt # 그래프 그를 때 사용하는 라이브러리
from matplotlib import font_manager # 폰트를 설정하기 위한 모듈

# 한글 폰트 설정
font_path = './malgun.ttf' # 사용할 한글 폰트 파일 경로
font_name = font_manager.FontProperties(fname = font_path).get_name()
plt.rc('font', family = 'NanumBarunGothic') # Matplotlib에서 폰트 지정
## 워드 클라우드는 기본적으로 영어 폰트만 지원, 한글 글꼴 지정은 필수

# 의미없는 단어(불용어) 제거
stop_words = ['구미','젤리', '맛있다.']

# 데이터 불러오기
df = pd.read_csv('./cleaned_data/cleaned_supplements.csv') # 정제된 리뷰 데이터 불러오기
print(df.head(10)) # 앞부분 출력해 확인

# 특정 문장 선택 및 전처리 
sentence = df.iloc[320,3] # 리뷰의 'reviews' 컬럼 내용 가져오기
# words = df.iloc[0, 1].split().split()

# 불용어 리스트에 있는 단어들을 모두 빈 문자열로 치환(삭제)
for stop_word in stop_words:
    sentence = sentence.replace(stop_word, '')
print(sentence) # 정제된 문장 출력

# 단어 빈도수 계산
words = sentence.split() # 공백을 기준으로 단어 분리

# word 딕셔너리, 어떤 단어가 몇번 나왔는지 확인
worddict = collections.Counter(words) # 단어 등장 횟수를 세어서 딕셔너리 형태로 저장
worddict = dict(worddict)
print(worddict) # 어떤 단어가 몇번 등장 했는지 확인

# 워드 클라우드 생성
wordcloud_img = WordCloud(
    # 배경색 흰색, # 최대 단어수, # 한글폰트 설정
    background_color = 'white', max_words = 2000, font_path= font_path
).generate_from_frequencies(worddict) # 단어-빈도 딕셔너리로부터 생성

# 워드 클라우드 시각화
plt.figure(figsize=(12,12)) # 이미지 크기 설정
plt.imshow(wordcloud_img, interpolation= 'bilinear') # 이미지 부드럽게 표시
plt.axis('off') # x, y 축 제거
plt.show()  # 이미지 화면에 출력
# 글씨가 클수록 많이 나오는 단어들 # 영화라는 단어를 봤을 때 리뷰를 기반으로 추천시스템에는 큰 도움이 안됨
# -> 그렇다면 제거하는것이 좋지 않은가? # 이런단어들을 살펴보는것이 중요(영화, 감독, 배우, ... 이런 단어들이 비슷한 영화들을 찾는데 도움이 안됨)


