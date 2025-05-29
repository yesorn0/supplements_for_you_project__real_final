import pandas as pd
import re
from konlpy.tag import Okt

# 1. 데이터 불러오기
df = pd.read_csv('./cleaned_data/all_supplements.csv')
print(df.info())
print(df.head())

# 2. 형태소 분석기 준비
okt = Okt()
cleaned_sentences = []

# 3. 불용어 설정
stop_words = [
    # 일반 동사/형용사
    '하다', '되다', '있다', '없다', '같다', '보다', '주다', '먹다', '좋다', '나쁘다',
    '많다', '적다', '크다', '작다', '들다', '꾸준하다', '훌륭하다', '탁월하다',
    '만족하다', '넘다', '들어서다', '안되다', '좋아하다', '되어다', '깔끔하다', '해보다',
    '해주다', '먹이다', '먹어주다', '아니다', '재다', '넘어가다', '사다', '빠르다',
    '켜지다', '다만', '비싸다', '기다리다', '특별하다', '꼼꼼하다', '이다', '어렵다',
    '않다', '먹기', '부분', '챙기다', '맛있다'

    # 명사
    '제품', '영양제', '구매', '구입', '사용', '가격', '포장', '배송', '리뷰',
    '후기', '품절', '유기농', '직구', '함량', '냄새', '부담', '구미', '젤리',

    # 수량, 시간, 기타
    '하루', '개월', '이상', '정도', '전', '후', '지금', '조금', '다시', '계속',
    '처음', '최근', '현재', '매일', '늘', '함께',

    # 신체/감정 추상어
    '느낌', '기분', '만족', '불만',
]

# 4. 1글자라도 유지할 중요한 단어들
preserve_words = ['A', 'B', 'C', 'D', 'E', 'K', '손', '발', '목', '몸',
                  '눈', '팔', '간', '장', '뇌', '뼈', '귀', '코',
                  '위', '폐', '피']

# 5. 리뷰 하나씩 처리
for review in df['review']:
    review = review.replace('|', ' ')  # 구분자 제거
    review = re.sub('[^가-힣A-Za-z]', ' ', review)  # 한글/영문 외 문자 제거

    # 형태소 분석 + 원형 복원
    tokens = okt.pos(review, stem=True)

    words = []
    for w, cls in tokens:
        if w in preserve_words:
            words.append(w)  # 무조건 포함
        elif cls in ['Noun', 'Adjective', 'Verb'] and len(w) > 1 and w not in stop_words:
            words.append(w)

    cleaned = ' '.join(words)
    print(cleaned)  # 중간 확인용
    cleaned_sentences.append(cleaned)

# 6. 결과 저장
df['review'] = cleaned_sentences
df.drop_duplicates(subset=['review'], inplace=True)  # 중복 제거
df.to_csv('./cleaned_data/cleaned_supplements.csv', index=False, encoding='utf-8-sig')
print("✅ 불용어 필터링 및 1글자 키워드 유지 전처리 완료")
