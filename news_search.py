import requests
import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict
from config import NEWS_API_KEY, SEARCH_LANGUAGE, SEARCH_DAYS, MAX_NEWS_COUNT, TRUSTED_SOURCES

class NewsSearcher:
    def __init__(self):
        self.news_api_key = NEWS_API_KEY
        self.search_days = SEARCH_DAYS
        
    def search_news(self, company: str) -> List[Dict]:
        """
        특정 회사에 대한 최근 뉴스를 검색합니다.
        
        Args:
            company (str): 검색할 회사명
            
        Returns:
            List[Dict]: 뉴스 리스트
        """
        news_list = []
        
        # NewsAPI를 통한 검색 (한국어 + 영어)
        if self.news_api_key and self.news_api_key != 'your_news_api_key_here':
            news_list.extend(self._search_newsapi(company, 'ko'))  # 한국어 뉴스
            news_list.extend(self._search_newsapi(company, 'en'))  # 영어 뉴스
        
        # RSS 피드를 통한 검색 (백업)
        news_list.extend(self._search_rss_feeds(company))
        
        # 중복 제거 및 정렬
        news_list = self._deduplicate_news(news_list)
        news_list = news_list[:MAX_NEWS_COUNT]
        
        return news_list
    
    def _search_newsapi(self, company: str, language: str = 'ko') -> List[Dict]:
        """NewsAPI를 통한 뉴스 검색"""
        news_list = []
        
        try:
            # 최근 24시간 계산
            from_date = (datetime.now() - timedelta(days=self.search_days)).strftime('%Y-%m-%d')
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': company,
                'from': from_date,
                'language': language,
                'sortBy': 'publishedAt',
                'apiKey': self.news_api_key,
                'pageSize': 50
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            for article in data.get('articles', []):
                news_item = {
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'company': company
                }
                news_list.append(news_item)
                
        except Exception as e:
            print(f"NewsAPI 검색 중 오류 발생: {e}")
            
        return news_list
    
    def _search_rss_feeds(self, company: str) -> List[Dict]:
        """RSS 피드를 통한 뉴스 검색"""
        news_list = []
        
        # 주요 경제 뉴스 RSS 피드 (한국 + 해외)
        rss_feeds = [
            # 해외 뉴스
            'https://feeds.reuters.com/reuters/businessNews',
            'https://feeds.bloomberg.com/markets/news.rss',
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'https://feeds.bbci.co.uk/news/business/rss.xml',
            'https://rss.cnn.com/rss/money_latest.rss',
            'https://feeds.marketwatch.com/marketwatch/topstories/',
            # 한국 뉴스 (RSS 피드가 있는 경우)
            'https://rss.joins.com/joins_news_list.xml',
            'https://rss.donga.com/total.xml'
        ]
        
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    # 회사명이 제목이나 요약에 포함된 경우만
                    if (company.lower() in entry.title.lower() or 
                        company.lower() in entry.get('summary', '').lower()):
                        
                        news_item = {
                            'title': entry.title,
                            'description': entry.get('summary', ''),
                            'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '',
                            'url': entry.link,
                            'source': feed.feed.get('title', 'RSS Feed'),
                            'published_at': entry.get('published', ''),
                            'company': company
                        }
                        news_list.append(news_item)
                        
            except Exception as e:
                print(f"RSS 피드 {feed_url} 검색 중 오류: {e}")
                
        return news_list
    
    def _deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """중복 뉴스 제거"""
        seen_urls = set()
        unique_news = []
        
        for news in news_list:
            if news['url'] not in seen_urls:
                seen_urls.add(news['url'])
                unique_news.append(news)
                
        return unique_news
    
    def get_news_content(self, url: str) -> str:
        """뉴스 URL에서 전체 내용을 추출합니다."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 일반적인 뉴스 기사 태그들
            content_selectors = [
                'article',
                '.article-content',
                '.news-content',
                '.story-content',
                'main',
                '.content'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text(strip=True) for elem in elements])
                    break
            
            if not content:
                # 모든 텍스트 추출
                content = soup.get_text(strip=True)
            
            return content[:2000]  # 최대 2000자로 제한
            
        except Exception as e:
            print(f"뉴스 내용 추출 중 오류: {e}")
            return ""
