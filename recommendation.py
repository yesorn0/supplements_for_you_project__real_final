import pandas as pd
import pickle
import json
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import linear_kernel
from scipy.io import mmread



# ------------------- 1. 모델 및 데이터 로딩 -------------------
df_products = pd.read_csv('./models/tfidf_products.csv')
tfidf_matrix = mmread('./models/tfidf_supplements.mtx').tocsr()
with open('./models/tfidf.pickle', 'rb') as f:
    tfidf = pickle.load(f)
embedding_model = Word2Vec.load('./models/word2vec_supplements_review.model')


# 증상 → 추천 키워드
with open('./knowledge/mapping.json', 'r', encoding='utf-8') as f:
    symptom_mapping = json.load(f)

# 증상 → 피해야 할 키워드
with open('./knowledge/avoid_mapping.json', 'r', encoding='utf-8') as f:
    avoid_mapping = json.load(f)

# ------------------- 2. 증상 입력 -------------------
input_symptoms = ['시력저하']  # 다중 입력 가능

# 중요도 가중치 문장 생성 함수
def build_weighted_sentence(keywords):
    sentence = []
    weight = len(keywords)
    for word in keywords:
        sentence.extend([word] * weight)
        weight -= 1
    return ' '.join(sentence)

# 추천 함수 (피해야 할 성분 고려)
def recommend_for_symptom(symptom, topn=5):
    # 키워드 매핑
    keywords = symptom_mapping.get(symptom, [symptom])
    avoid_words = avoid_mapping.get(symptom, [])

    # 중요도 가중 문장 생성
    query_sentence = build_weighted_sentence(keywords)

    # 유사도 계산
    query_vec = tfidf.transform([query_sentence])
    cosine_sim = linear_kernel(query_vec, tfidf_matrix)

    # 유사 제품 추천
    sim_scores = list(enumerate(cosine_sim[-1]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # 필터링 (설명에 피해야 할 성분 포함 시 제외)
    filtered_indices = []
    for idx, score in sim_scores:
        desc = df_products.iloc[idx]['ingredient']  # 또는 'ingredient' 컬럼 등 설명 텍스트
        if not any(bad in desc for bad in avoid_words):
            filtered_indices.append(idx)
        if len(filtered_indices) == topn:
            break

    return df_products.iloc[filtered_indices]

# ------------------- 3. 증상별 출력 -------------------
for symptom in input_symptoms:
    recommend_df = recommend_for_symptom(symptom, topn=5)
    print(f"\n✅ 증상 '{symptom}' 관련 추천 영양제 {len(recommend_df)}개:\n")
    for idx, row in recommend_df.iterrows():
        print(f"- {row['product']}")
