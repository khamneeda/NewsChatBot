#!/usr/bin/env python3
"""
주식 뉴스 검색 및 요약 챗봇

이 챗봇은 특정 회사에 대한 최근 뉴스를 검색하고,
중요도 순으로 정렬하여 요약해주는 기능을 제공합니다.

사용법:
    python stock_news_chatbot.py

또는

    from stock_news_chatbot import StockNewsChatbot
    chatbot = StockNewsChatbot()
    result = chatbot.search_and_summarize("삼성전자")
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
import openai

# 로컬 모듈 import
from news_search import NewsSearcher
from importance_evaluator import ImportanceEvaluator
from summarizer import NewsSummarizer
from config import OPENAI_API_KEY, MODEL_NAME, TARGET_COMPANY

class StockNewsChatbot:
    def __init__(self):
        """주식 뉴스 챗봇 초기화"""
        # OpenAI API 설정
        openai.api_key = OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # 모듈 초기화
        self.news_searcher = NewsSearcher()
        self.importance_evaluator = ImportanceEvaluator()
        self.summarizer = NewsSummarizer()
        
        print("🚀 주식 뉴스 챗봇이 초기화되었습니다!")
        print(f"📊 사용 모델: {MODEL_NAME}")
        print("=" * 50)
    
    def search_and_summarize(self, company: str) -> Dict:
        """
        특정 회사에 대한 뉴스를 검색하고 요약합니다.
        
        Args:
            company (str): 검색할 회사명
            
        Returns:
            Dict: 검색 결과 및 요약 정보
        """
        print(f"🔍 '{company}'에 대한 최근 뉴스를 검색 중...")
        
        try:
            # 1. 뉴스 검색
            news_list = self.news_searcher.search_news(company)
            
            if not news_list:
                return {
                    'company': company,
                    'search_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_news': 0,
                    'message': f"'{company}'에 대한 최근 뉴스를 찾을 수 없습니다.",
                    'news_list': [],
                    'overall_summary': ""
                }
            
            print(f"📰 총 {len(news_list)}개의 뉴스를 찾았습니다.")
            
            # 2. 중요도 평가
            print("⚖️ 뉴스 중요도를 평가 중...")
            evaluated_news = self.importance_evaluator.evaluate_news_importance(news_list)
            
            # 3. 뉴스 요약
            print("📝 뉴스를 요약 중...")
            summarized_news = self.summarizer.summarize_news(evaluated_news)
            
            # 4. 종합 요약 생성
            print("🎯 종합 요약을 생성 중...")
            overall_summary = self.summarizer.generate_overall_summary(summarized_news)
            # print(f"DEBUG: 생성된 종합 요약: '{overall_summary}'")
            
            result = {
                'company': company,
                'search_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_news': len(news_list),
                'message': f"'{company}'에 대한 {len(news_list)}개의 뉴스를 분석했습니다.",
                'news_list': summarized_news,
                'overall_summary': overall_summary
            }
            
            print("✅ 분석이 완료되었습니다!")
            return result
            
        except Exception as e:
            print(f"❌ 오류가 발생했습니다: {e}")
            return {
                'company': company,
                'search_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_news': 0,
                'message': f"오류가 발생했습니다: {str(e)}",
                'news_list': [],
                'overall_summary': ""
            }
    
    def display_results(self, result: Dict):
        """
        검색 결과를 보기 좋게 출력합니다.
        
        Args:
            result (Dict): search_and_summarize의 결과
        """
        print("\n" + "=" * 60)
        print(f"📊 {result['company']} 뉴스 분석 결과")
        print("=" * 60)
        print(f"🕐 검색 시간: {result['search_time']}")
        print(f"📰 총 뉴스 수: {result['total_news']}개")
        print(f"💬 {result['message']}")
        
        if result.get('overall_summary'):
            print("\n🎯 종합 요약")
            print("-" * 40)
            print(result['overall_summary'])
        else:
            print("\n🎯 종합 요약")
            print("-" * 40)
            print("종합 요약이 생성되지 않았습니다.")
        
        if result['news_list']:
            print(f"\n📋 중요도 순 뉴스 목록 (상위 {min(10, len(result['news_list']))}개)")
            print("-" * 40)
            
            for i, news in enumerate(result['news_list'][:10]):
                print(f"\n{i+1}. {news.get('title', '제목 없음')}")
                print(f"   📰 출처: {news.get('source', '알 수 없음')}")
                print(f"   ⭐ 중요도: {news.get('final_score', 0):.2f}")
                print(f"   📅 발행일: {news.get('published_at', '알 수 없음')}")
                
                if news.get('summary'):
                    print(f"   📝 요약: {news.get('summary', '')}")
                
                if news.get('url'):
                    print(f"   🔗 링크: {news.get('url', '')}")
                
                print("-" * 40)
    
    # def interactive_mode(self):
    #     """대화형 모드로 챗봇을 실행합니다."""
    #     print("\n🎉 주식 뉴스 챗봇 대화형 모드")
    #     print("=" * 50)
    #     print("사용법:")
    #     print("- 회사명을 입력하면 해당 회사의 최근 뉴스를 분석합니다")
    #     print("- 'quit', 'exit', '종료'를 입력하면 프로그램을 종료합니다")
    #     print("- 'help'를 입력하면 도움말을 볼 수 있습니다")
    #     print("=" * 50)
    #     
    #     while True:
    #         try:
    #             user_input = input("\n🔍 분석할 회사명을 입력하세요: ").strip()
    #             
    #             if not user_input:
    #                 print("❌ 회사명을 입력해주세요.")
    #                 continue
    #             
    #             # 종료 명령어
    #             if user_input.lower() in ['quit', 'exit', '종료', 'q']:
    #                 print("👋 주식 뉴스 챗봇을 종료합니다. 감사합니다!")
    #                 break
    #             
    #             # 도움말
    #             if user_input.lower() in ['help', '도움말', 'h']:
    #                 self._show_help()
    #                 continue
    #             
    #             # 뉴스 검색 및 분석
    #             result = self.search_and_summarize(user_input)
    #             self.display_results(result)
    #             
    #         except KeyboardInterrupt:
    #             print("\n\n👋 사용자가 프로그램을 종료했습니다.")
    #             break
    #         except Exception as e:
    #             print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")
    
    # def _show_help(self):
    #     """도움말을 표시합니다."""
    #     print("\n📚 주식 뉴스 챗봇 도움말")
    #     print("-" * 30)
    #     print("🔍 기능:")
    #     print("  - 특정 회사의 최근 24시간 뉴스 검색")
    #     print("  - 뉴스 중요도 평가 (신뢰성, 중대성, 빈도)")
    #     print("  - AI 기반 뉴스 요약")
    #     print("  - 중요도 순 정렬")
    #     print("\n💡 사용 예시:")
    #     print("  - 삼성전자")
    #     print("  - SK하이닉스")
    #     print("  - 네이버")
    #     print("  - 카카오")
    #     print("\n⚙️ 중요도 평가 기준:")
    #     print("  - 신뢰성 (40%): 뉴스 소스의 신뢰도")
    #     print("  - 중대성 (40%): 주가에 미치는 영향도")
    #     print("  - 빈도 (20%): 유사 뉴스의 빈도")

def main():
    """메인 함수"""
    try:
        # 챗봇 초기화
        chatbot = StockNewsChatbot()
        
        # 명령행 인수가 있으면 해당 회사 분석
        if len(sys.argv) > 1:
            company = sys.argv[1]
            result = chatbot.search_and_summarize(company)
            chatbot.display_results(result)
        else:
            # config.py에서 설정된 기업명으로 분석
            print(f"📊 설정된 기업명: {TARGET_COMPANY}")
            result = chatbot.search_and_summarize(TARGET_COMPANY)
            chatbot.display_results(result)
            
            # 추가 분석을 위한 대화형 모드 실행 (주석처리)
            # chatbot.interactive_mode()
            
    except Exception as e:
        print(f"❌ 프로그램 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
