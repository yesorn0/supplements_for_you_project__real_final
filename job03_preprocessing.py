import pandas as pd
import re
from konlpy.tag import Okt
import time
from multiprocessing import Pool, cpu_count
import numpy as np

# 1. 데이터 불러오기
df = pd.read_csv('./cleaned_data/all_supplements.csv')
print(df.info())
print(df.head())

# 0번째 열: 영양제 종류 정제 (띄어쓰기 제거 + 명칭 통일)
df.iloc[:, 0] = df.iloc[:, 0].str.replace(' ', '', regex=False)  # 모든 공백 제거

# 명칭 통일
df.iloc[:, 0] = df.iloc[:, 0].replace({
    '남성용비타민': '남성종합비타민',
    '남성용종합비타민': '남성종합비타민',
    '여성용비타민': '여성종합비타민',
    '여성용종합비타민': '여성종합비타민',
    '멀티비타민': '종합비타민',
    '남성멀티비타민': '남성종합비타민',
    '여성멀티비타민': '여성종합비타민',
    '임산부종합비타민': '임산부종합비타민',
})

print("\n✅ 정제된 영양제 종류 고유값:")
print(df.iloc[:, 0].unique())

# 2. 성능 최적화를 위한 설정
print(f"사용 가능한 CPU 코어 수: {cpu_count()}")

# 3. 불용어를 set으로 변환 (검색 속도 O(1))
stop_words = set([
    # 일반 동사/형용사
    '하다', '되다', '있다', '없다', '같다', '보다', '주다', '먹다', '좋다', '나쁘다',
    '많다', '적다', '크다', '작다', '들다', '꾸준하다', '훌륭하다', '탁월하다',
    '만족하다', '넘다', '들어서다', '안되다', '좋아하다', '되어다', '깔끔하다', '해보다',
    '해주다', '먹이다', '먹어주다', '아니다', '재다', '넘어가다', '사다', '빠르다',
    '켜지다', '다만', '비싸다', '기다리다', '특별하다', '꼼꼼하다', '이다', '어렵다',
    '않다', '먹기', '부분', '챙기다', '맛있다',
    # 명사
    '제품', '영양제', '구매', '구입', '사용', '가격', '포장', '배송', '리뷰',
    '후기', '품절', '유기농', '직구', '함량', '냄새', '부담', '구미', '젤리',
    # 수량, 시간, 기타
    '하루', '개월', '이상', '정도', '전', '후', '지금', '조금', '다시', '계속',
    '처음', '최근', '현재', '매일', '늘', '함께',
    # 신체/감정 추상어
    '느낌', '기분', '만족', '불만',
])

# 4. preserve_words도 set으로 변환
preserve_words = set(['A', 'B', 'C', 'D', 'E', 'K', '손', '발', '목', '몸', '눈',
                      '팔', '간', '장', '뇌', '뼈', '귀', '코', '위', '폐', '피'])

# 5. 정규표현식 컴파일 (성능 향상)
vitamin_patterns = [
    (re.compile(r'비타민\s*([AaBbCcDdEeKk])', re.IGNORECASE), r'비타민\1'),
    (re.compile(r'비타민([a-z])'), lambda m: f'비타민{m.group(1).upper()}'),
    (re.compile(r'비타민\s*[Bb]\s*(\d+)'), r'비타민B\1'),
    (re.compile(r'[Vv]itamin\s*([AaBbCcDdEeKk])'), r'비타민\1'),
    (re.compile(r'비타민\s*디\s*(?:3|three)', re.IGNORECASE), '비타민D'),
    (re.compile(r'비타민\s*씨', re.IGNORECASE), '비타민C'),
]

special_char_pattern = re.compile('[^가-힣A-Za-z0-9]')


def normalize_vitamins_optimized(text):
    """최적화된 비타민 표기 정규화 함수"""
    if pd.isna(text) or text == '':
        return text

    text = str(text)

    # 컴파일된 정규표현식 사용
    for pattern, replacement in vitamin_patterns:
        if callable(replacement):
            text = pattern.sub(replacement, text)
        else:
            text = pattern.sub(replacement, text)

    return text


def process_single_review(review_data):
    """단일 리뷰 처리 함수 (멀티프로세싱용)"""
    idx, review = review_data

    if pd.isna(review):
        return idx, ''

    try:
        review = str(review)
        review = review.replace('|', ' ')

        # 비타민 표기 정규화 (lower() 전에)
        review = normalize_vitamins_optimized(review)

        review = review.lower()

        # 특수문자 제거 (컴파일된 패턴 사용)
        review = special_char_pattern.sub(' ', review)

        # 빈 문자열 체크
        if not review.strip():
            return idx, ''

        # 형태소 분석
        okt = Okt()  # 각 프로세스마다 새로운 인스턴스
        tokens = okt.pos(review, stem=True)

        words = []
        for w, cls in tokens:
            if w in preserve_words:
                words.append(w)
            elif cls in ['Noun', 'Adjective', 'Verb'] and len(w) > 1 and w not in stop_words:
                words.append(w)

        cleaned = ' '.join(words)
        return idx, cleaned

    except Exception as e:
        print(f"오류 발생 (인덱스 {idx}): {e}")
        return idx, ''


def process_reviews_batch(reviews_batch):
    """배치 단위로 리뷰 처리"""
    results = []
    okt = Okt()  # 배치당 하나의 인스턴스

    for idx, review in reviews_batch:
        if pd.isna(review):
            results.append((idx, ''))
            continue

        try:
            review = str(review)
            review = review.replace('|', ' ')

            # 비타민 표기 정규화
            review = normalize_vitamins_optimized(review)

            review = review.lower()
            review = special_char_pattern.sub(' ', review)

            if not review.strip():
                results.append((idx, ''))
                continue

            tokens = okt.pos(review, stem=True)

            words = []
            for w, cls in tokens:
                if w in preserve_words:
                    words.append(w)
                elif cls in ['Noun', 'Adjective', 'Verb'] and len(w) > 1 and w not in stop_words:
                    words.append(w)

            cleaned = ' '.join(words)
            results.append((idx, cleaned))

            # 진행상황 출력
            if idx % 50 == 0:
                print(f"배치 처리 중... {idx}")
                print(f"결과: {cleaned}")

        except Exception as e:
            print(f"오류 발생 (인덱스 {idx}): {e}")
            results.append((idx, ''))

    return results


# 6. 메인 처리 로직
print(f"\n🚀 총 {len(df)} 개의 리뷰 처리 시작...")
start_time = time.time()

# 배치 크기 설정 (메모리와 성능의 균형)
batch_size = 50
total_reviews = len(df)
batches = []

# 배치 생성
for i in range(0, total_reviews, batch_size):
    batch = [(idx, review) for idx, review in enumerate(df['review'].iloc[i:i + batch_size], i)]
    batches.append(batch)

print(f"총 {len(batches)}개 배치로 분할")

# 배치별 처리 (멀티프로세싱 대신 순차 처리로 안정성 확보)
all_results = []
for batch_idx, batch in enumerate(batches):
    print(f"\n배치 {batch_idx + 1}/{len(batches)} 처리 중...")
    batch_results = process_reviews_batch(batch)
    all_results.extend(batch_results)

    # 중간 진행률 표시
    progress = (batch_idx + 1) / len(batches) * 100
    elapsed_time = time.time() - start_time
    print(f"진행률: {progress:.1f}% | 경과시간: {elapsed_time:.1f}초")

# 결과 정렬 및 적용
all_results.sort(key=lambda x: x[0])  # 인덱스 순으로 정렬
cleaned_sentences = [result[1] for result in all_results]

# 7. 저장
df['review'] = cleaned_sentences
print(f"\n중복 제거 전: {len(df)}개")
df.drop_duplicates(subset=['review'], inplace=True)
print(f"중복 제거 후: {len(df)}개")

df.to_csv('./cleaned_data/cleaned_supplements.csv', index=False, encoding='utf-8-sig')

end_time = time.time()
total_time = end_time - start_time
print(f"\n✅ 리뷰 전처리 완료! 총 소요시간: {total_time:.1f}초")
print(f"평균 처리속도: {len(df) / total_time:.2f}개/초")

# 8. 정규화 결과 확인
print("\n✅ 비타민 표기 정규화 테스트:")
test_cases = [
    "비타민 a가 좋아요",
    "비타민 A 효과",
    "vitamin c 추천",
    "비타민 디3",
    "비타민 씨",
    "비타민B 12",
    "비타민 b1 복합체"
]

for test in test_cases:
    normalized = normalize_vitamins_optimized(test)
    print(f"'{test}' → '{normalized}'")