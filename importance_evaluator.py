import re
import time
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import openai
from config import TRUSTED_SOURCES, WEIGHTS, OPENAI_API_KEY, MODEL_NAME, TEMPERATURE, IMPORTANCE_KEYWORDS

class ImportanceEvaluator:
    def __init__(self):
        self.weights = WEIGHTS
        self.trusted_sources = TRUSTED_SOURCES
        self.importance_keywords = IMPORTANCE_KEYWORDS
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL_NAME
        self.temperature = TEMPERATURE
        
    def evaluate_news_importance(self, news_list: List[Dict]) -> List[Dict]:
        """
        뉴스의 중요도를 평가합니다.
        
        Args:
            news_list (List[Dict]): 뉴스 리스트
            
        Returns:
            List[Dict]: 중요도 점수가 추가된 뉴스 리스트
        """
        if not news_list:
            return []
        
        # 각 뉴스에 중요도 점수 계산
        for news in news_list:
            reliability_score = self._calculate_reliability_score(news)
            impact_score = self._calculate_llm_impact_score(news)
            frequency_score = self._calculate_frequency_score(news, news_list)
            
            # 가중 평균으로 최종 점수 계산
            final_score = (
                reliability_score * self.weights['reliability'] +
                impact_score * self.weights['impact'] +
                frequency_score * self.weights['frequency']
            )
            
            news['reliability_score'] = reliability_score
            news['impact_score'] = impact_score
            news['frequency_score'] = frequency_score
            news['final_score'] = final_score
        
        return news_list
    
    def _calculate_reliability_score(self, news: Dict) -> float:
        """
        뉴스의 신뢰성을 평가합니다.
        
        Args:
            news (Dict): 뉴스 정보
            
        Returns:
            float: 신뢰성 점수 (0-1)
        """
        source = news.get('source', '').lower()
        
        # 한국 신뢰할 수 있는 소스인지 확인
        for trusted_source in self.trusted_sources['korean']:
            if trusted_source.lower() in source:
                return 1.0
        
        # 해외 신뢰할 수 있는 소스인지 확인
        for trusted_source in self.trusted_sources['international']:
            if trusted_source.lower() in source:
                return 0.9
        
        # 일반적인 뉴스 소스
        if any(keyword in source for keyword in ['news', 'times', 'post', 'herald', 'daily']):
            return 0.7
        
        # 블로그나 개인 사이트
        if any(keyword in source for keyword in ['blog', 'personal', 'wordpress']):
            return 0.3
        
        # 기본 점수
        return 0.5
    
    def _calculate_llm_impact_score(self, news: Dict) -> float:
        """
        LLM을 사용하여 뉴스의 중대성(주가 영향도)을 평가합니다.
        
        Args:
            news (Dict): 뉴스 정보
            
        Returns:
            float: 중대성 점수 (0-1)
        """
        title = news.get('title', '')
        description = news.get('description', '')
        content = news.get('content', '')
        
        # 평가할 텍스트 구성
        text_to_evaluate = f"제목: {title}\n\n내용: {description}\n\n본문: {content[:1000]}"
        
        # 중요도 키워드들을 프롬프트에 포함
        keywords_text = f"""
높은 영향도 키워드: {', '.join(self.importance_keywords['high_impact'])}
중간 영향도 키워드: {', '.join(self.importance_keywords['medium_impact'])}
낮은 영향도 키워드: {', '.join(self.importance_keywords['low_impact'])}
"""
        
        prompt = f"""
다음 뉴스의 주가에 미치는 영향도를 0-1 사이의 점수로 평가해주세요.

{keywords_text}

평가 기준:
- 0.8-1.0: 매우 높은 영향 (실적 발표, 인수합병, 신제품 출시, CEO 교체 등)
- 0.6-0.8: 높은 영향 (투자, 파트너십, 규제 승인, 공시 등)
- 0.4-0.6: 중간 영향 (시장 동향, 경쟁사 관련, 고객 계약 등)
- 0.2-0.4: 낮은 영향 (이벤트 참가, 인터뷰, 의견 발표 등)
- 0.0-0.2: 매우 낮은 영향 (일반적인 업계 뉴스, 개인적 활동 등)

뉴스 내용:
{text_to_evaluate}

점수만 숫자로 답변해주세요 (예: 0.75):
"""
        
        try:
            # Rate limit 방지를 위한 지연
            time.sleep(1)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 주식 투자 분석 전문가입니다. 뉴스의 주가 영향도를 정확하게 평가합니다."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            
            # 점수 추출 및 검증
            try:
                score = float(score_text)
                # 0-1 범위로 제한
                score = max(0.0, min(1.0, score))
                return score
            except ValueError:
                # 숫자 변환 실패 시 기본 점수 반환
                return 0.5
                
        except Exception as e:
            print(f"LLM 중요도 평가 중 오류: {e}")
            # 오류 시 키워드 기반 평가로 폴백
            return self._fallback_impact_score(news)
    
    def _fallback_impact_score(self, news: Dict) -> float:
        """LLM 오류 시 사용할 키워드 기반 평가"""
        title = news.get('title', '').lower()
        description = news.get('description', '').lower()
        content = news.get('content', '').lower()
        
        text = f"{title} {description} {content}"
        
        # 키워드 점수 계산
        high_score = sum(1 for keyword in self.importance_keywords['high_impact'] if keyword.lower() in text)
        medium_score = sum(1 for keyword in self.importance_keywords['medium_impact'] if keyword.lower() in text)
        low_score = sum(1 for keyword in self.importance_keywords['low_impact'] if keyword.lower() in text)
        
        # 가중 점수 계산
        total_score = (high_score * 3 + medium_score * 2 + low_score * 1)
        
        # 정규화 (0-1 범위)
        max_possible_score = len(self.importance_keywords['high_impact']) * 3
        normalized_score = min(total_score / max_possible_score, 1.0) if max_possible_score > 0 else 0.5
        
        return normalized_score
    
    def _calculate_frequency_score(self, news: Dict, all_news: List[Dict]) -> float:
        """
        유사한 뉴스의 빈도를 계산합니다.
        
        Args:
            news (Dict): 현재 뉴스
            all_news (List[Dict]): 전체 뉴스 리스트
            
        Returns:
            float: 빈도 점수 (0-1)
        """
        if len(all_news) <= 1:
            return 0.5
        
        # 텍스트 벡터화
        texts = [f"{n.get('title', '')} {n.get('description', '')}" for n in all_news]
        current_text = f"{news.get('title', '')} {news.get('description', '')}"
        
        try:
            vectorizer = TfidfVectorizer(max_features=100, stop_words=None)
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # 현재 뉴스와 다른 뉴스들의 유사도 계산
            current_vector = vectorizer.transform([current_text])
            similarities = cosine_similarity(current_vector, tfidf_matrix)[0]
            
            # 자기 자신 제외하고 유사도 계산
            similarities = np.delete(similarities, np.argmax(similarities))
            
            # 유사도가 높은 뉴스 개수 계산 (임계값: 0.3)
            similar_count = np.sum(similarities > 0.3)
            
            # 빈도 점수 계산 (유사한 뉴스가 많을수록 높은 점수)
            max_similar = len(all_news) - 1
            frequency_score = similar_count / max_similar if max_similar > 0 else 0
            
            return min(frequency_score, 1.0)
            
        except Exception as e:
            print(f"빈도 점수 계산 중 오류: {e}")
            return 0.5
