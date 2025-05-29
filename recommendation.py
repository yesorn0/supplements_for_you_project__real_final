import pandas as pd
import pickle
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import linear_kernel
from scipy.io import mmread
from konlpy.tag import Okt
import re

# ------------------- 1. 모델 및 데이터 로딩 -------------------
df_products = pd.read_csv('./models/tfidf_products.csv')
tfidf_matrix = mmread('./models/tfidf_supplements.mtx').tocsr()
with open('./models/tfidf.pickle', 'rb') as f:
    tfidf = pickle.load(f)
embedding_model = Word2Vec.load('./models/word2vec_supplements_combined.model')  # <-- 파일명 확인!

# ------------------- 2. 한글 형태소 분석기 준비 -------------------
okt = Okt()

# ------------------- 3. 증상 키워드 입력 -------------------
input_symptoms = ['시력']  # 예시 증상


# ------------------- 4. 리뷰에서 직접 키워드 기반 추천 -------------------
def recommend_by_review(symptom_query, topn=5):
    results = []
    # 증상 키워드에서 명사만 추출
    tokens = okt.nouns(symptom_query)
    for idx, row in df_products.iterrows():
        review = row.get('review', '')
        if not isinstance(review, str):
            continue
        # 리뷰 텍스트에서 명사만 추출
        review_nouns = okt.nouns(re.sub(r'[^가-힣a-zA-Z0-9]', ' ', review))
        if any(token in review_nouns for token in tokens):
            results.append(row)
        if len(results) >= topn:
            break
    return pd.DataFrame(results)


# ------------------- 5. Word2Vec로 의미적으로 가까운 단어로 확장 추천 -------------------
def expand_symptom_by_word2vec(symptom_query, topn_word=5):
    tokens = okt.nouns(symptom_query)
    expanded = set(tokens)
    for token in tokens:
        if token in embedding_model.wv:
            # 증상과 유사한 단어 topn_word개 뽑기
            similar_words = [w for w, s in embedding_model.wv.most_similar(token, topn=topn_word)]
            expanded.update(similar_words)
    return list(expanded)


def recommend_by_review_word2vec(symptom_query, topn=5, expand_topn_word=5):
    # Word2Vec을 통해 증상과 의미적으로 가까운 단어 확장
    expanded_tokens = expand_symptom_by_word2vec(symptom_query, topn_word=expand_topn_word)
    results = []
    for idx, row in df_products.iterrows():
        review = row.get('review', '')
        if not isinstance(review, str):
            continue
        review_nouns = okt.nouns(re.sub(r'[^가-힣a-zA-Z0-9]', ' ', review))
        if any(token in review_nouns for token in expanded_tokens):
            results.append(row)
        if len(results) >= topn:
            break
    return pd.DataFrame(results)


# ------------------- 6. 출력 (리뷰 기반 / Word2Vec 기반) -------------------
for symptom in input_symptoms:
    print(f"\n[리뷰에 직접 키워드 등장하는 추천]")
    recommend_df = recommend_by_review(symptom, topn=5)
    for idx, row in recommend_df.iterrows():
        print(f"- {row['product']}")

    print(f"\n[Word2Vec 의미적 유사 키워드까지 확장 추천]")
    recommend_df2 = recommend_by_review_word2vec(symptom, topn=5)
    for idx, row in recommend_df2.iterrows():
        print(f"- {row['product']}")

print("\n✅ 추천 완료")
