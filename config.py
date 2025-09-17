import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 설정
OPENAI_API_KEY = "OPENAI_API_KEY"

# 뉴스 API 설정 (NewsAPI 사용 예시)
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your_news_api_key_here')

# 모델 설정
MODEL_NAME = "gpt-5"
TEMPERATURE = 0.3

# 뉴스 검색 설정
SEARCH_LANGUAGE = "ko"  # 한국어 뉴스
SEARCH_DAYS = 1  # 최근 1일
MAX_NEWS_COUNT = 50  # 최대 뉴스 개수

# 분석할 기업명 설정
TARGET_COMPANY = "Nvidia"  # 분석할 기업명 (변경 가능)

# 중요도 평가 가중치
WEIGHTS = {
    'reliability': 0.4,  # 신뢰성
    'impact': 0.4,       # 중대성
    'frequency': 0.2     # 빈도
}

# 신뢰할 수 있는 뉴스 소스 (한국 + 해외)
TRUSTED_SOURCES = {
    'korean': [
        '연합뉴스', '뉴스1', '뉴시스', '매일경제', '한국경제', 
        '조선일보', '중앙일보', '동아일보', '한겨레', '경향신문',
        '이데일리', '아시아경제', '헤럴드경제', '서울경제', '파이낸셜뉴스'
    ],
    'international': [
        'Reuters', 'Bloomberg', 'Wall Street Journal', 'Financial Times',
        'CNN Business', 'BBC Business', 'CNBC', 'MarketWatch',
        'Yahoo Finance', 'Forbes', 'Business Insider', 'The Guardian',
        'Associated Press', 'Dow Jones', 'New York Times Business'
    ]
}

# LLM 기반 중요도 평가를 위한 키워드
IMPORTANCE_KEYWORDS = {
    'high_impact': [
        'earnings', 'revenue', 'profit', 'quarterly results', 'annual results',
        'merger', 'acquisition', 'M&A', 'partnership', 'investment',
        'new product', 'launch', 'patent', 'technology', 'R&D',
        'regulation', 'government', 'policy', 'approval', 'license',
        'CEO', 'executive', 'leadership', 'management change',
        'disclosure', 'announcement', 'press release', 'conference call'
    ],
    'medium_impact': [
        'market', 'competition', 'competitor', 'industry', 'trend',
        'customer', 'client', 'contract', 'order', 'deal',
        'facility', 'expansion', 'construction', 'manufacturing',
        'hiring', 'recruitment', 'workforce', 'employee'
    ],
    'low_impact': [
        'event', 'conference', 'participation', 'visit', 'meeting',
        'interview', 'statement', 'opinion', 'outlook', 'forecast'
    ]
}
