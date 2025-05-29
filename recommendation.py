import pandas as pd
import re
from konlpy.tag import Okt
from gensim.models import Word2Vec
from functools import lru_cache


# ------------------- 하이브리드 토큰화 -------------------
class HybridTokenizer:
    def __init__(self):
        self.okt = Okt()
        self.pattern = re.compile(r'[^가-힣a-zA-Z0-9]')

    @lru_cache(maxsize=1000)
    def tokenize_smart(self, text):
        """짧은 텍스트는 형태소 분석, 긴 텍스트는 띄어쓰기"""
        if pd.isna(text) or text == '':
            return frozenset()

        text = str(text)

        # 길이 기준으로 처리 방법 결정
        if len(text) < 100:  # 짧은 텍스트 (제품명 등)
            cleaned = self.pattern.sub(' ', text)
            return frozenset(self.okt.nouns(cleaned))
        else:  # 긴 텍스트 (리뷰 등)
            # 띄어쓰기 + 간단한 전처리
            cleaned = self.pattern.sub(' ', text)
            tokens = [token for token in cleaned.split() if len(token) > 1]
            return frozenset(tokens)

    def tokenize_simple(self, text):
        """단순 띄어쓰기 분할 (기존 방식)"""
        if pd.isna(text) or text == '':
            return frozenset()

        cleaned = self.pattern.sub(' ', str(text))
        tokens = [token for token in cleaned.split() if len(token) > 1]
        return frozenset(tokens)


# ------------------- 최적화된 전처리 -------------------
def preprocess_data_optimized(df):
    tokenizer = HybridTokenizer()

    print("🔍 제품명 토큰화 중...")
    df['product_tokens'] = df['product'].apply(tokenizer.tokenize_smart)

    print("🔍 리뷰 토큰화 중...")
    # 리뷰는 길어서 단순 방식 사용
    df['review_tokens'] = df['review'].apply(tokenizer.tokenize_simple)

    return df


# ------------------- Word2Vec 확장 (기존과 동일) -------------------
@lru_cache(maxsize=128)
def expand_symptom_by_word2vec(symptom_query, embedding_model, topn_word=8):
    tokenizer = HybridTokenizer()
    tokens = list(tokenizer.tokenize_smart(symptom_query))
    expanded = set(tokens)

    for token in tokens:
        if token in embedding_model.wv:
            try:
                similar_words = [w for w, _ in embedding_model.wv.most_similar(token, topn=topn_word)]
                expanded.update(similar_words)
            except KeyError:
                continue

    return frozenset(expanded)


# ------------------- 추천 함수 -------------------
def recommend_products_hybrid(df, symptom_query, embedding_model, topn=5):
    expanded_tokens = expand_symptom_by_word2vec(symptom_query, embedding_model)
    print(f"🔍 확장된 키워드: {expanded_tokens}")

    # 벡터화된 점수 계산
    def calculate_score(row):
        review_score = len(expanded_tokens & row['review_tokens'])
        product_score = len(expanded_tokens & row['product_tokens']) * 2  # 제품명 가중치
        return review_score + product_score

    df['temp_score'] = df.apply(calculate_score, axis=1)
    result = df[df['temp_score'] > 0].nlargest(topn, 'temp_score')
    df.drop('temp_score', axis=1, inplace=True)

    return result


# ------------------- 실행 예시 -------------------
if __name__ == "__main__":
    # 데이터 로딩
    df_products = pd.read_csv('./models/tfidf_products.csv')
    embedding_model = Word2Vec.load('./models/word2vec_supplements_okt.model')

    # 전처리 (한 번만 실행)
    df_products = preprocess_data_optimized(df_products)

    # 추천 실행
    symptoms = ['골다공증', '눈건조증']
    for symptom in symptoms:
        print(f"\n✅ [{symptom}] 추천 결과:")
        result = recommend_products_hybrid(df_products, symptom, embedding_model)
        for _, row in result.iterrows():
            print(f"- {row['product']} (점수: {row.get('temp_score', 'N/A')})")