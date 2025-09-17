import openai
import time
from typing import List, Dict
from config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE

class NewsSummarizer:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL_NAME
        self.temperature = TEMPERATURE
    
    def summarize_news(self, news_list: List[Dict]) -> List[Dict]:
        """
        뉴스 리스트를 요약합니다.
        
        Args:
            news_list (List[Dict]): 중요도 점수가 포함된 뉴스 리스트
            
        Returns:
            List[Dict]: 요약이 추가된 뉴스 리스트
        """
        if not news_list:
            return []
        
        # 중요도 순으로 정렬
        sorted_news = sorted(news_list, key=lambda x: x.get('final_score', 0), reverse=True)
        
        # 상위 뉴스들에 대해 요약 생성
        for i, news in enumerate(sorted_news[:10]):  # 상위 10개만 요약
            try:
                summary = self._generate_summary(news)
                news['summary'] = summary
                news['rank'] = i + 1
            except Exception as e:
                print(f"뉴스 요약 중 오류 발생: {e}")
                news['summary'] = news.get('description', '')[:200] + "..."
                news['rank'] = i + 1
        
        return sorted_news
    
    def _generate_summary(self, news: Dict) -> str:
        """
        개별 뉴스를 요약합니다.
        
        Args:
            news (Dict): 뉴스 정보
            
        Returns:
            str: 요약된 내용
        """
        title = news.get('title', '')
        description = news.get('description', '')
        content = news.get('content', '')
        company = news.get('company', '')
        
        # 요약할 텍스트 구성
        text_to_summarize = f"제목: {title}\n\n내용: {description}\n\n본문: {content[:1000]}"
        
        prompt = f"""
다음은 {company} 회사에 대한 뉴스입니다. 
주식 투자자 관점에서 핵심 내용을 한국어로 3-4문장으로 요약해주세요.

{text_to_summarize}

요약 시 다음 사항을 고려해주세요:
1. 회사의 실적이나 사업에 미치는 영향
2. 주가에 영향을 줄 수 있는 핵심 정보
3. 투자자들이 주목해야 할 포인트

반드시 한국어로 요약해주세요:
"""
        
        try:
            # Rate limit 방지를 위한 지연
            time.sleep(1)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 주식 투자 분석 전문가입니다. 뉴스를 투자자 관점에서 간결하고 명확하게 한국어로 요약합니다."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"OpenAI API 호출 중 오류: {e}")
            # API 오류 시 간단한 요약 생성
            return self._fallback_summary(news)
    
    def _fallback_summary(self, news: Dict) -> str:
        """API 오류 시 사용할 간단한 요약"""
        title = news.get('title', '')
        description = news.get('description', '')
        
        # 간단한 요약 생성
        summary = f"{title}"
        if description:
            summary += f" - {description[:150]}..."
        
        return summary
    
    def generate_overall_summary(self, news_list: List[Dict]) -> str:
        """
        전체 뉴스에 대한 종합 요약을 생성합니다.
        
        Args:
            news_list (List[Dict]): 요약된 뉴스 리스트
            
        Returns:
            str: 종합 요약
        """
        if not news_list:
            return "해당 회사에 대한 최근 뉴스가 없습니다."
        
        # 상위 5개 뉴스의 요약을 종합
        top_news = news_list[:5]
        summaries = [news.get('summary', '') for news in top_news if news.get('summary')]
        
        # 요약이 없는 경우 제목과 설명으로 대체
        if not summaries:
            summaries = []
            for news in top_news:
                title = news.get('title', '')
                description = news.get('description', '')
                if title or description:
                    summaries.append(f"제목: {title}\n내용: {description}")
        
        if not summaries:
            return "분석할 수 있는 뉴스 내용이 없습니다."
        
        # print(f"DEBUG: 종합 요약을 위한 {len(summaries)}개의 요약/뉴스 발견")
        
        combined_text = "\n\n".join([f"{i+1}. {summary}" for i, summary in enumerate(summaries)])
        
        prompt = f"""
다음은 특정 회사에 대한 최근 뉴스 요약들입니다. 
이를 바탕으로 투자자들이 알아야 할 핵심 포인트를 한국어로 종합적으로 정리해주세요.

{combined_text}

종합 요약 시 다음을 포함해주세요:
1. 가장 중요한 뉴스 2-3개
2. 회사 전반적인 상황
3. 투자 관점에서의 시사점

반드시 한국어로 종합 요약해주세요:
"""
        
        try:
            # Rate limit 방지를 위한 지연
            time.sleep(1)
            
            # print("DEBUG: 종합 요약 API 호출 시작")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 주식 투자 분석 전문가입니다. 여러 뉴스를 종합하여 투자자에게 유용한 인사이트를 한국어로 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            # print(f"DEBUG: 종합 요약 생성 완료: '{result}'")
            # print(f"DEBUG: 종합 요약 길이: {len(result)}")
            
            # 빈 응답인 경우 폴백 사용
            if not result or len(result.strip()) == 0:
                # print("DEBUG: 빈 응답으로 인해 폴백 요약 사용")
                return self._fallback_overall_summary(news_list)
            
            return result
            
        except Exception as e:
            print(f"종합 요약 생성 중 오류: {e}")
            return "종합 요약을 생성할 수 없습니다."
    
    def _fallback_overall_summary(self, news_list: List[Dict]) -> str:
        """API 오류 시 사용할 간단한 종합 요약"""
        if not news_list:
            return "분석할 뉴스가 없습니다."
        
        top_news = news_list[:3]  # 상위 3개 뉴스
        summary_parts = []
        
        for i, news in enumerate(top_news, 1):
            title = news.get('title', '')
            score = news.get('final_score', 0)
            source = news.get('source', '')
            
            summary_parts.append(f"{i}. {title} (중요도: {score:.2f}, 출처: {source})")
        
        return f"주요 뉴스 요약:\n\n" + "\n\n".join(summary_parts)
