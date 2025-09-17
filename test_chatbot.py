#!/usr/bin/env python3
"""
주식 뉴스 챗봇 테스트 스크립트

이 스크립트는 챗봇의 각 모듈을 개별적으로 테스트합니다.
"""

import sys
import os
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock_news_chatbot import StockNewsChatbot
from news_search import NewsSearcher
from importance_evaluator import ImportanceEvaluator
from summarizer import NewsSummarizer
from config import OPENAI_API_KEY, TARGET_COMPANY

def test_news_search():
    """뉴스 검색 모듈 테스트"""
    print("뉴스 검색 모듈 테스트")
    print("-" * 30)
    
    try:
        searcher = NewsSearcher()
        test_company = TARGET_COMPANY
        
        print(f"'{test_company}'에 대한 뉴스 검색 중...")
        news_list = searcher.search_news(test_company)
        
        print(f"검색 완료: {len(news_list)}개의 뉴스 발견")
        
        if news_list:
            print("\n첫 번째 뉴스 예시:")
            first_news = news_list[0]
            print(f"  제목: {first_news.get('title', 'N/A')}")
            print(f"  출처: {first_news.get('source', 'N/A')}")
            print(f"  URL: {first_news.get('url', 'N/A')[:50]}...")
        
        return news_list
        
    except Exception as e:
        print(f"뉴스 검색 테스트 실패: {e}")
        return []

def test_importance_evaluator(news_list):
    """중요도 평가 모듈 테스트"""
    print("\n중요도 평가 모듈 테스트")
    print("-" * 30)
    
    if not news_list:
        print("테스트할 뉴스가 없습니다.")
        return []
    
    try:
        evaluator = ImportanceEvaluator()
        
        print(f"{len(news_list)}개 뉴스의 중요도 평가 중...")
        evaluated_news = evaluator.evaluate_news_importance(news_list)
        
        print("중요도 평가 완료")
        
        # 상위 3개 뉴스의 점수 출력
        sorted_news = sorted(evaluated_news, key=lambda x: x.get('final_score', 0), reverse=True)
        
        print("\n상위 3개 뉴스 점수:")
        for i, news in enumerate(sorted_news[:3]):
            print(f"  {i+1}. {news.get('title', 'N/A')[:30]}...")
            print(f"     최종점수: {news.get('final_score', 0):.3f}")
            print(f"     신뢰성: {news.get('reliability_score', 0):.3f}")
            print(f"     중대성: {news.get('impact_score', 0):.3f}")
            print(f"     빈도: {news.get('frequency_score', 0):.3f}")
        
        return evaluated_news
        
    except Exception as e:
        print(f"중요도 평가 테스트 실패: {e}")
        return news_list

def test_summarizer(news_list):
    """요약 모듈 테스트"""
    print("\n요약 모듈 테스트")
    print("-" * 30)
    
    if not news_list:
        print("테스트할 뉴스가 없습니다.")
        return []
    
    try:
        summarizer = NewsSummarizer()
        
        print(f"{len(news_list)}개 뉴스 요약 중...")
        summarized_news = summarizer.summarize_news(news_list)
        
        print("뉴스 요약 완료")
        
        # 첫 번째 뉴스의 요약 출력
        if summarized_news and summarized_news[0].get('summary'):
            print("\n첫 번째 뉴스 요약 예시:")
            print(f"  제목: {summarized_news[0].get('title', 'N/A')}")
            print(f"  요약: {summarized_news[0].get('summary', 'N/A')[:200]}...")
        
        return summarized_news
        
    except Exception as e:
        print(f"요약 테스트 실패: {e}")
        return news_list

def test_full_workflow():
    """전체 워크플로우 테스트"""
    print("\n전체 워크플로우 테스트")
    print("=" * 50)
    
    try:
        chatbot = StockNewsChatbot()
        test_company = TARGET_COMPANY
        
        print(f"'{test_company}'에 대한 전체 분석 시작...")
        result = chatbot.search_and_summarize(test_company)
        
        print("전체 워크플로우 완료")
        
        # 결과 요약 출력
        print(f"\n분석 결과:")
        print(f"  회사: {result['company']}")
        print(f"  총 뉴스 수: {result['total_news']}")
        print(f"  검색 시간: {result['search_time']}")
        
        if result['overall_summary']:
            print(f"  종합 요약: {result['overall_summary'][:100]}...")
        
        return result
        
    except Exception as e:
        print(f"전체 워크플로우 테스트 실패: {e}")
        return None

def main():
    """메인 테스트 함수"""
    print("주식 뉴스 챗봇 테스트 시작")
    print("=" * 50)
    
    # API 키 확인
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        print("OpenAI API 키가 설정되지 않았습니다.")
        print("config.py 파일에서 OPENAI_API_KEY를 설정해주세요.")
        return
    
    # 개별 모듈 테스트
    news_list = test_news_search()
    evaluated_news = test_importance_evaluator(news_list)
    summarized_news = test_summarizer(evaluated_news)
    
    # 전체 워크플로우 테스트
    result = test_full_workflow()
    
    print("\n모든 테스트 완료!")
    print("=" * 50)
    
    if result:
        print("챗봇이 정상적으로 작동합니다.")
        print("\n사용법:")
        print("  python stock_news_chatbot.py")
        print("  또는")
        print("  python stock_news_chatbot.py '회사명'")
    else:
        print("일부 테스트에서 문제가 발생했습니다.")
        print("설정을 확인하고 다시 시도해주세요.")

if __name__ == "__main__":
    main()
