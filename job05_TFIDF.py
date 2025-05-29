import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.io import mmwrite
import os
import logging
from pathlib import Path
import time
from typing import Tuple, Optional
import warnings

# 경고 메시지 필터링
warnings.filterwarnings('ignore')


class TFIDFProcessor:
    """TF-IDF 벡터화 처리를 위한 클래스"""

    def __init__(self,
                 input_path: str = './cleaned_data/cleaned_supplements.csv',
                 output_dir: str = './models',
                 log_level: str = 'INFO'):
        """
        초기화

        Args:
            input_path: 입력 CSV 파일 경로
            output_dir: 출력 디렉토리 경로
            log_level: 로그 레벨 ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        """
        self.input_path = input_path
        self.output_dir = Path(output_dir)
        self.df_review = None
        self.df_grouped = None
        self.tfidf = None
        self.tfidf_matrix = None

        # 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 로깅 설정
        self._setup_logging(log_level)

    def _setup_logging(self, log_level: str) -> None:
        """로깅 설정"""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'tfidf_process.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_data(self) -> pd.DataFrame:
        """데이터 로드 및 검증"""
        self.logger.info(f"📂 데이터 로드 중: {self.input_path}")

        try:
            df = pd.read_csv(self.input_path)
            self.logger.info(f"✅ 데이터 로드 완료: {len(df):,}개 행")

            # 필수 컬럼 검증
            required_cols = ['review', 'product', 'ingredient', 'url']
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                raise ValueError(f"필수 컬럼 누락: {missing_cols}")

            return df

        except FileNotFoundError:
            self.logger.error(f"❌ 파일을 찾을 수 없습니다: {self.input_path}")
            raise
        except Exception as e:
            self.logger.error(f"❌ 데이터 로드 실패: {e}")
            raise

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 정제"""
        self.logger.info("🧹 데이터 정제 중...")

        initial_count = len(df)

        # 결측치 제거 (더 효율적인 방법)
        required_cols = ['review', 'product', 'ingredient', 'url']
        df_clean = df.dropna(subset=required_cols)

        # 빈 문자열 제거
        for col in required_cols:
            df_clean = df_clean[df_clean[col].str.strip() != '']

        # 중복 제거 (제품명+리뷰 기준)
        df_clean = df_clean.drop_duplicates(subset=['product', 'review'])

        removed_count = initial_count - len(df_clean)
        self.logger.info(f"✅ 정제 완료: {removed_count:,}개 행 제거, {len(df_clean):,}개 행 유지")

        return df_clean

    def group_reviews(self, df: pd.DataFrame) -> pd.DataFrame:
        """제품별 리뷰 그룹화"""
        self.logger.info("📊 제품별 리뷰 그룹화 중...")
        start_time = time.time()

        # 제품별 통계 정보 추가
        product_stats = df.groupby('product').agg({
            'review': ['count', lambda x: ' '.join(x)],
            'ingredient': 'first',
            'url': 'first'
        }).reset_index()

        # 컬럼명 정리
        product_stats.columns = ['product', 'review_count', 'review', 'ingredient', 'url']

        # 리뷰 길이 정보 추가
        product_stats['review_length'] = product_stats['review'].str.len()
        product_stats['avg_review_length'] = product_stats['review_length'] / product_stats['review_count']

        elapsed_time = time.time() - start_time
        self.logger.info(f"✅ 그룹화 완료: {len(product_stats):,}개 제품, {elapsed_time:.2f}초 소요")

        return product_stats

    def create_tfidf_matrix(self, df: pd.DataFrame, **tfidf_params) -> Tuple[TfidfVectorizer, any]:
        """TF-IDF 행렬 생성"""
        self.logger.info("🔢 TF-IDF 벡터화 중...")
        start_time = time.time()

        # 기본 파라미터 설정
        default_params = {
            'sublinear_tf': True,
            'max_features': 10000,  # 메모리 효율성을 위한 제한
            'min_df': 2,  # 최소 2번 등장하는 단어만
            'max_df': 0.8,  # 80% 이상 문서에 등장하는 단어 제외
            'ngram_range': (1, 2)  # 1-gram, 2-gram 모두 사용
        }
        default_params.update(tfidf_params)

        try:
            tfidf = TfidfVectorizer(**default_params)
            tfidf_matrix = tfidf.fit_transform(df['review'])

            elapsed_time = time.time() - start_time

            # 행렬 정보 출력
            self.logger.info(f"✅ TF-IDF 완료:")
            self.logger.info(f"   - 행렬 크기: {tfidf_matrix.shape}")
            self.logger.info(f"   - 특성 수: {len(tfidf.get_feature_names_out()):,}")
            self.logger.info(
                f"   - 희소성: {(1 - tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1])) * 100:.2f}%")
            self.logger.info(f"   - 소요 시간: {elapsed_time:.2f}초")

            return tfidf, tfidf_matrix

        except Exception as e:
            self.logger.error(f"❌ TF-IDF 벡터화 실패: {e}")
            raise

    def save_results(self, df: pd.DataFrame, tfidf: TfidfVectorizer, tfidf_matrix) -> None:
        """결과 저장"""
        self.logger.info("💾 결과 저장 중...")

        try:
            # 1. TF-IDF 모델 저장
            with open(self.output_dir / 'tfidf.pickle', 'wb') as f:
                pickle.dump(tfidf, f)
            self.logger.info("✅ TF-IDF 모델 저장 완료")

            # 2. TF-IDF 행렬 저장 (Matrix Market 형식)
            mmwrite(str(self.output_dir / 'tfidf_supplements.mtx'), tfidf_matrix)
            self.logger.info("✅ TF-IDF 행렬 저장 완료")

            # 3. 제품 정보 저장 (통계 정보 포함)
            output_cols = ['product', 'review', 'ingredient', 'url', 'review_count', 'review_length',
                           'avg_review_length']
            df[output_cols].to_csv(
                self.output_dir / 'tfidf_products.csv',
                index=False,
                encoding='utf-8-sig'
            )
            self.logger.info("✅ 제품 정보 저장 완료")

            # 4. 특성(단어) 목록 저장
            feature_names = tfidf.get_feature_names_out()
            pd.DataFrame({'feature': feature_names}).to_csv(
                self.output_dir / 'tfidf_features.csv',
                index=False,
                encoding='utf-8-sig'
            )
            self.logger.info("✅ 특성 목록 저장 완료")

            # 5. 메타데이터 저장
            metadata = {
                'total_products': len(df),
                'matrix_shape': tfidf_matrix.shape,
                'feature_count': len(feature_names),
                'sparsity': (1 - tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1])) * 100,
                'processing_date': pd.Timestamp.now().isoformat()
            }

            pd.DataFrame([metadata]).to_csv(
                self.output_dir / 'tfidf_metadata.csv',
                index=False
            )
            self.logger.info("✅ 메타데이터 저장 완료")

        except Exception as e:
            self.logger.error(f"❌ 저장 실패: {e}")
            raise

    def generate_report(self, df: pd.DataFrame) -> None:
        """처리 결과 리포트 생성"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("📊 처리 결과 요약")
        self.logger.info("=" * 50)

        # 기본 통계
        self.logger.info(f"총 제품 수: {len(df):,}")
        self.logger.info(f"총 리뷰 수: {df['review_count'].sum():,}")
        self.logger.info(f"평균 제품당 리뷰 수: {df['review_count'].mean():.1f}")

        # 리뷰 길이 통계
        self.logger.info(f"평균 리뷰 길이: {df['avg_review_length'].mean():.0f}자")
        self.logger.info(f"최장 리뷰 길이: {df['review_length'].max():,}자")

        # 상위 제품 (리뷰 수 기준)
        top_products = df.nlargest(5, 'review_count')[['product', 'review_count']]
        self.logger.info("\n🏆 리뷰 수 상위 5개 제품:")
        for _, row in top_products.iterrows():
            self.logger.info(f"   {row['product']}: {row['review_count']}개")

        self.logger.info("=" * 50)

    def process(self, **tfidf_params) -> None:
        """전체 처리 파이프라인 실행"""
        total_start_time = time.time()

        try:
            # 1. 데이터 로드
            self.df_review = self.load_data()

            # 2. 데이터 정제
            self.df_review = self.clean_data(self.df_review)

            # 3. 리뷰 그룹화
            self.df_grouped = self.group_reviews(self.df_review)

            # 4. TF-IDF 벡터화
            self.tfidf, self.tfidf_matrix = self.create_tfidf_matrix(self.df_grouped, **tfidf_params)

            # 5. 결과 저장
            self.save_results(self.df_grouped, self.tfidf, self.tfidf_matrix)

            # 6. 리포트 생성
            self.generate_report(self.df_grouped)

            total_elapsed_time = time.time() - total_start_time
            self.logger.info(f"\n🎉 전체 처리 완료! 총 소요시간: {total_elapsed_time:.2f}초")

        except Exception as e:
            self.logger.error(f"❌ 처리 중 오류 발생: {e}")
            raise


def main():
    """메인 실행 함수"""
    # TF-IDF 파라미터 커스터마이징 가능
    tfidf_params = {
        'max_features': 15000,
        'min_df': 3,
        'max_df': 0.7,
        'ngram_range': (1, 2)
    }

    processor = TFIDFProcessor(
        input_path='./cleaned_data/cleaned_supplements.csv',
        output_dir='./models',
        log_level='INFO'
    )

    processor.process(**tfidf_params)


if __name__ == "__main__":
    main()