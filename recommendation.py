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

# symptom to keywords mapping 불러오기
with open('./knowledge/mapping.json', 'r', encoding='utf-8') as f:
    symptom_mapping = json.load(f)

# ------------------- 2. 증상 입력 -------------------
input_symptoms = ['']  # 다중 입력 가능

# 중요도 가중치 문장 생성 함수
def build_weighted_sentence(keywords):
    sentence = []
    weight = len(keywords)
    for word in keywords:
        sentence.extend([word] * weight)
        weight -= 1
    return ' '.join(sentence)

# 추천 함수
def recommend_for_symptom(symptom, topn=5):
    # 정확한 키 기반 매핑
    keywords = symptom_mapping.get(symptom, [symptom])

    # 의미 확장 (Word2Vec) + 필터링
    # if symptom in embedding_model.wv:
    #     sim_words = embedding_model.wv.most_similar(symptom, topn=20)
    #     allow_prefix = ['피로', '피곤', '피부', '피지', '피멍']
    #     filtered_words = [
    #         w for w, _ in sim_words
    #         if not (w == '피' or (w.startswith('피') and w not in allow_prefix))
    #     ]
    #     keywords.extend(filtered_words[:5])

    # 중요도 가중 문장 생성
    query_sentence = build_weighted_sentence(keywords)

    # 유사도 계산
    query_vec = tfidf.transform([query_sentence])
    cosine_sim = linear_kernel(query_vec, tfidf_matrix)

    # 유사 제품 추천
    sim_scores = list(enumerate(cosine_sim[-1]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[:topn]
    indices = [idx for idx, _ in sim_scores]
    return df_products.iloc[indices]


# ------------------- 3. 증상별 출력 -------------------
for symptom in input_symptoms:
    recommend_df = recommend_for_symptom(symptom, topn=5)
    print(f"\n✅ 증상 '{symptom}' 관련 추천 영양제 {len(recommend_df)}개:\n")
    for idx, row in recommend_df.iterrows():
        print(f"- {row['product']}")



