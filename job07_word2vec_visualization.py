# 원래 데이터의 손실을 최소화하는 방향으로 차원축소

import pandas as pd
import matplotlib.pyplot as plt
from gensim.models import word2vec, Word2Vec
from numpy.distutils.misc_util import cyan_text
from sklearn.manifold import TSNE
from matplotlib import font_manager, rc
import matplotlib as mpl

font_path = './malgun.ttf'
font_name = font_manager.FontProperties(fname=font_path).get_name()
mpl.rcParams['axes.unicode_minus'] = False
rc('font', family = font_name)

embedding_model = Word2Vec.load('./models/word2vec_movie_review.model')
key_word = ('사랑') # 학습한 단어가 없으면 에러가 발생
sim_word = embedding_model.wv.most_similar(key_word, topn= 10) # 공간적으로 가까이 있는 단어를 의미(여기서 공간은 좌표를 말함)
print(sim_word)

vectors = []
labels = []
for label, _ in sim_word:
    labels.append(label)
    vectors.append(embedding_model.wv[label])
print(labels[0])
print(vectors[0])
print(len(vectors[0]))

# 차원축소해서 시각화
df_vectors = pd.DataFrame(vectors)
print(df_vectors.head())

tsne_model = TSNE(perplexity =9, n_components= 2, init= 'pca', n_iter = 2500)
new_value = tsne_model.fit_transform(df_vectors)
df_xy = pd.DataFrame({'words':labels, 'x':new_value[:,0],
                     'y':new_value[:, 1]})
df_xy.loc[df_xy.shape[0]] = (key_word, 0, 0)
print(df_xy)
print(df_xy.shape)

plt.figure(figsize = (8, 8))
plt.scatter(0,0, s= 1500, marker = '*')
for i in range(len(df_xy)):
    a = df_xy.loc[[i, 10]]
    plt.plot(a.x, a.y, '-D', linewidth = 1)
    plt.annotate(df_xy.words[i], xytext = (1,1), xy=(df_xy.x[i], df_xy.y[i]),
                    textcoords = 'offset points', ha='right', va ='bottom')

plt.show()

# 여름처럼 싱그럽고 뜨거운 영화를 찾으려면?  # 지금은 키워드 1개만 가지고 추천중