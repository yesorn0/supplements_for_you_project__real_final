import sys # 시스템 종료 등 시스템 관련 기능 사용
import pandas as pd # CSV 등의 데이터 파일 읽고 다루기 위한 라이브러리
from PyQt5.QtWidgets import * # 버튼, 콤보박스 등 위젯 사용을 위한 PyQt 클래스들 import
from PyQt5 import uic # Qt Designer에서 만든 .ui 파일을 파이썬 코드로 불러오기 위한 도구
from PyQt5.QtCore import QCoreApplication, QStringListModel # 응용 프로그램 기본 기능 + 문자열 리스트 모델 사용
from PyQt5.QtCore import QStringListModel # 자도오안성 기능을 위한 위젯
from gensim.models import Word2Vec # 단어 벡터 모델(자연어 의미 분석용)
from scipy.io import mmread # 희소행렬 파일(.mtx) 읽기
from sklearn.metrics.pairwise import linear_kernel  # 벡터 간 유사도 계산 함수
import pickle # 파이썬 객체를 파일로 저장하거나 불러오기 위한 모듈

# Qt 디자이너로 만든 .ui파일을 불러와 python 클래스 형태로 변환
form_window = uic.loadUiType('./movie_recommendation.ui')[0] # Qt Designer로 만든 Ui 파일을 클래스 형태로 불러옴

# ------------------------------------------------------------------------------------------------------------------
# 메인 윈도우 클래스 정의
# QWidget : 모든 PyQt 위젯의 기반 클래스
# form_window : 불러온 UI 클래스
class Exam(QWidget, form_window):
    def __init__(self): # 생성자 함수
        super().__init__()  # 부모 클래스 초기화
        self.setupUi(self)  # .ui파일 내 위젯들을 현재 클래스와 연결

# ------------------------------------------------------------------------------------------------------------------
# 모델 로딩 및 데이터 준비        
        # TF-IDF로 벡터화된 영화 리뷰 데이터 불러오기 (희소 행렬)
        self.tfidf_matrix = mmread('./models/tfidf_movie_review.mtx').tocsr() # mtx는 tocsr을 해줘야함 -> 알아보기
        # TF-IDF 벡터화에 사용된 벡터라이저 객체 불러오기
        with open('./models/tfidf.pickle', 'rb') as f:
            self.tfidf = pickle.load(f)
            
        # Word2Vec 모델(단어 유사도 계산용) 로드
        self.embedding_model = Word2Vec.load('./models/word2vec_movie_review.model')
       # 전처리된 영화 제목과 리뷰 데이터를 불러옴
        self.df_reviews = pd.read_csv('./cleaned_data/cleaned_reviews.csv')
        self.titles = list(self.df_reviews['titles']) # 영화 제목만 리스트로 추출
        self.titles.sort() # 가나다 순으로 정렬
        for title in self.titles: # 콤보박스에 영화 제목 추가
            self.comboBox.addItem(title)

# ------------------------------------------------------------------------------------------------------------------
# 자동완성 기능 연결
        # 자동완성을 위한 문자열 모델 생성
        model = QStringListModel()
        model.setStringList(self.titles) # 영화 제목 목록 등록
        
        # QCompleter 객체 생성 및 모델 등록
        completer =QCompleter()
        completer.setModel(model)
        
        # 키워드 입력창에 자동완성 기능 적용
        self.le_keyword.setCompleter(completer)

# ------------------------------------------------------------------------------------------------------------------
# 이벤트 연결
        self.comboBox.currentIndexChanged.connect(self.combobox_slot) # 콤보박스가 바뀔 때 함수 연결
        self.btn_recommendation.clicked.connect(self.btn_slot) # 추천 버튼 클릭 시 함수 연결

# ------------------------------------------------------------------------------------------------------------------
# 버튼 클릭 시 동작 정의
    def btn_slot(self):
        # 키워드 입력창에서 텍스트 가져오기
        user_input = self.le_keyword.text() # 사용자 입력 테스트 가져오기
        
        # 입력한 텍스트가 영화 제목 리스트에 포함된다면, 해당 영화 기준 추천
        if user_input in self.titles:
            self.movie_title_recomm(user_input)
        # 포함되지 않는다면 키워드 기반 추천(단어의 의미 기반 유사도)
        else:
            self.keyword_slot(user_input.split()[0]) # 첫 단어만 사용

    # ------------------------------------------------------------------------------------------------------------------
    # 키워드 기반 추천 함수

    def keyword_slot(self, keyword):
        sim_word = self.embedding_model.wv.most_similar(keyword, topn=10) # Word2Vec을 통해 유사 단어 top 10 가져오기
        # 유사 단어들을 모아서 리스트로 저장
        words = [keyword]
        for word, _ in sim_word:
            words.append(word)
        # 단어들을 가중치(빈도) 기분으로 문자 구성
        sentence = []
        count = 10
        for word in words:
            sentence = sentence + [word] * count # 단어의 중요도에 따라 반복 횟수 다르게
            count -= 1
            
        # 단어 리스트를 하나의 문자열로 합침
        sentence = ' '.join((sentence))
        print(sentence) # 디버깅용 출력

        # 문장을 TF-IDF 벡터로 변환
        sentence_vec = self.tfidf.transform([sentence])
        # 전체 영화와의 코사인 유사도 계산
        cosine_sim = linear_kernel(sentence_vec, self.tfidf_matrix)
        
        # 추천 결과 리스트 가져오기
        recommendation = self.getRecommendation(cosine_sim)
        print(recommendation)
        print(type(recommendation))
        # 추천 결과를 줄바꿈으로 묶어서 표시
        recommendation = '\n'.join(recommendation[:10])
        self.lbl_recommendation.setText(recommendation)

# ------------------------------------------------------------------------------------------------------------------
    def getRecommendation(self, cosine_sim):
        simScore = list(enumerate(cosine_sim[-1]))  # 각 영화의 유사도 점수와 인덱스를 리스트로 저장
        simScore = sorted(simScore, key=lambda x: x[1], reverse=True)  # 유사도가 높은 순으로 정렬
        simScore = simScore[:11]  # 자기 자신 + 유사한 영화 10개 선택
        movie_idx = [i[0] for i in simScore]  # 인덱스만 따로 저장
        # 해당 인덱스에 해당하는 영화 제목 리스트 추출
        rec_movie_list = self.df_reviews.iloc[movie_idx, 0]  # 제목 컬럼(index 0)을 기반으로 추천 목록 생성
        return rec_movie_list[:11]  # 자기 자신은 제외하고 10개만 반환

# ------------------------------------------------------------------------------------------------------------------
# 콤보박스 영화 선택 시 호출
    def combobox_slot(self):
        title = self.comboBox.currentText() # 현재 선택 된 영화 제목 가져오기
        self.movie_title_recomm(title) # 해당 영화 기준으로 추천 수행

# ------------------------------------------------------------------------------------------------------------------
# 영화 제목 기준 추천 함수
    def movie_title_recomm(self, title):
        # 선택된 영화 제목의 인덱스 찾기
        movie_idx = self.df_reviews[self.df_reviews['titles'] == title ].index[0]
        # TF-IDF 유사도 계산(선택한 영화 vs 전체 영화)
        cosine_sim = linear_kernel(self.tfidf_matrix[movie_idx],
                                   self.tfidf_matrix)
        
        recommendation = self.getRecommendation(cosine_sim) # 추천 결과 가져오기
        recommendation = '\n'.join(recommendation[1:]) # 자기자신은 제외하고 10개만 표시
        self.lbl_recommendation.setText(recommendation) # 라벨에 추천 결과 표시

# 메인함수(실행 시작점)
if __name__ == '__main__':
    app = QApplication(sys.argv)    # PyQt 애플리케이션 객체 생성
    mainWindow = Exam()             # 메인 윈도우 클래스 생성
    mainWindow.show()               # 윈도우 표시
    sys.exit(app.exec())            # 프로그램 종료까지 이벤트 루프 실행