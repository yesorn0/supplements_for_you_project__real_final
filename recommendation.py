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
input_symptom = '다한증, 피로'  # 사용자 입력 가능

# 증상 매핑 기반 키워드 추출
keywords = []
for category, key_list in symptom_mapping.items():
    if input_symptom in key_list:
        keywords.extend(key_list)
        break

# 매핑이 없으면 input_symptom 자체 사용
if not keywords:
    keywords = [input_symptom]

# 의미 확장 (Word2Vec 기반)
if input_symptom in embedding_model.wv:
    sim_words = embedding_model.wv.most_similar(input_symptom, topn=5)
    keywords.extend([w for w, _ in sim_words])

# 중요도 가중치 문장 생성
def build_weighted_sentence(keywords):
    sentence = []
    weight = len(keywords)
    for word in keywords:
        sentence.extend([word] * weight)
        weight -= 1
    return ' '.join(sentence)

query_sentence = build_weighted_sentence(keywords)

# ------------------- 3. 벡터화 및 유사도 계산 -------------------
query_vec = tfidf.transform([query_sentence])
cosine_sim = linear_kernel(query_vec, tfidf_matrix)

# ------------------- 4. 제품 추천 -------------------
def recommend_products(cosine_sim, topn=10):
    sim_scores = list(enumerate(cosine_sim[-1]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[:topn]
    indices = [idx for idx, _ in sim_scores]
    return df_products.iloc[indices]

# ------------------- 5. 출력 -------------------
recommend_df = recommend_products(cosine_sim)
print(f"\n✅ 증상 '{input_symptom}' 관련 추천 영양제 TOP {len(recommend_df)}개:\n")
for idx, row in recommend_df.iterrows():
    print(f"- {row['product']}")


