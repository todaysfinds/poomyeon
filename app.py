from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Database configuration
if os.getenv('DATABASE_URL'):
    # Production - PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
else:
    # Development - SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookclub.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Notion API configuration
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
NOTION_VERSION = '2022-06-28'

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Google Books API configuration
GOOGLE_BOOKS_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')

# Models
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Member {self.name}>'

# Notion API functions
def add_book_to_notion(book_data):
    """Add book record to Notion database"""
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        return False, "Notion API credentials not configured"
    
    url = f"https://api.notion.com/v1/pages"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }
    
    # Prepare data for Notion
    notion_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "이름": {
                "select": {
                    "name": book_data['member_name']
                }
            },
            "책 제목": {
                "title": [
                    {
                        "text": {
                            "content": book_data['title']
                        }
                    }
                ]
            },
            "저자": {
                "rich_text": [
                    {
                        "text": {
                            "content": book_data['author']
                        }
                    }
                ]
            },
            "장르": {
                "select": {
                    "name": book_data['genre']
                }
            },
            "완독 여부": {
                "checkbox": book_data['completed']
            },
            "별점": {
                "number": book_data['rating']
            },
            "한줄평": {
                "rich_text": [
                    {
                        "text": {
                            "content": book_data['review']
                        }
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=notion_data)
        if response.status_code == 200:
            return True, "Book successfully added to Notion"
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Error connecting to Notion: {str(e)}"

# Google Books API functions
def get_book_info_from_google(title, author=""):
    """Get book information from Google Books API"""
    if not GOOGLE_BOOKS_API_KEY:
        return None
    
    # Create search query
    query = f'"{title}"'
    if author:
        query += f' inauthor:"{author}"'
    
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': query,
        'key': GOOGLE_BOOKS_API_KEY,
        'maxResults': 1
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('totalItems', 0) > 0:
                book = data['items'][0]['volumeInfo']
                return {
                    'title': book.get('title', ''),
                    'authors': book.get('authors', []),
                    'description': book.get('description', ''),
                    'categories': book.get('categories', []),
                    'publishedDate': book.get('publishedDate', ''),
                    'pageCount': book.get('pageCount', 0)
                }
    except Exception as e:
        print(f"Error fetching from Google Books API: {str(e)}")
    
    return None

# GPT API functions
def create_keyword_prompt(book_info, user_genre, user_review=""):
    """Create a well-crafted prompt for GPT to generate discussion keywords"""
    
    if book_info:
        # Use Google Books data for rich context
        prompt = f"""
다음 책에 대한 독서모임 토론용 키워드를 3-5개 생성해주세요:

📚 책 정보:
- 제목: {book_info.get('title', '')}
- 저자: {', '.join(book_info.get('authors', []))}
- 장르: {user_genre}
- 설명: {book_info.get('description', '')[:500]}...
- 카테고리: {', '.join(book_info.get('categories', []))}
"""
        if user_review:
            prompt += f"- 독자 한줄평: {user_review}\n"
    else:
        # Fallback prompt with basic information
        prompt = f"""
다음 정보를 바탕으로 독서모임 토론용 키워드를 3-5개 생성해주세요:

📚 기본 정보:
- 장르: {user_genre}
"""
        if user_review:
            prompt += f"- 독자 한줄평: {user_review}\n"
    
    prompt += """
🎯 요구사항:
1. 독서모임에서 활발한 토론을 이끌어낼 수 있는 키워드
2. 책의 핵심 주제와 관련된 키워드
3. 개인적 경험과 연결할 수 있는 키워드
4. 간단하고 명확한 단어나 짧은 구문
5. 각 키워드는 2-4단어로 구성

출력 형식: 키워드만 쉼표로 구분하여 나열 (예: 성장, 인간관계, 꿈과 현실, 사회적 편견, 자아실현)
"""
    
    return prompt

def generate_keywords_with_gpt(book_title, author, genre, review=""):
    """Generate discussion keywords using GPT API"""
    
    if not openai_client:
        # Fallback keywords based on genre
        return get_fallback_keywords(genre)
    
    try:
        # First, try to get book info from Google Books
        book_info = get_book_info_from_google(book_title, author)
        
        # Create prompt
        prompt = create_keyword_prompt(book_info, genre, review)
        
        # Call GPT API
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "당신은 독서모임 전문가입니다. 책에 대한 깊이 있는 토론을 이끌어내는 키워드를 제안해주세요."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        keywords_text = response.choices[0].message.content.strip()
        keywords = [keyword.strip() for keyword in keywords_text.split(',')]
        
        # Clean up keywords and limit to 5
        cleaned_keywords = []
        for keyword in keywords[:5]:
            if keyword and len(keyword) > 0:
                cleaned_keywords.append(keyword)
        
        return cleaned_keywords
        
    except Exception as e:
        print(f"Error generating keywords with GPT: {str(e)}")
        return get_fallback_keywords(genre)

def get_fallback_keywords(genre):
    """Provide fallback keywords when APIs are not available"""
    fallback_map = {
        '소설': ['인물의 성장', '갈등과 해결', '인간관계', '감정의 변화', '상징과 의미'],
        '에세이': ['작가의 관점', '일상의 깨달음', '개인적 경험', '생각의 전환', '공감과 위로'],
        '자기계발': ['실천 방법', '변화의 계기', '목표 설정', '습관 형성', '성공과 실패'],
        '경제/경영': ['시장 변화', '비즈니스 전략', '투자 철학', '경제 트렌드', '성공 사례'],
        '역사': ['시대적 배경', '역사적 교훈', '인물의 선택', '사회 변화', '현재와의 연결'],
        '과학': ['과학적 발견', '기술의 발전', '미래 전망', '일상 속 과학', '윤리적 고민'],
        '철학': ['존재의 의미', '가치관 정립', '삶의 방향', '도덕과 윤리', '사고의 확장'],
        '예술': ['창작 과정', '미적 감각', '문화적 배경', '예술가 정신', '감상과 해석'],
        '기타': ['새로운 시각', '배움의 즐거움', '호기심 충족', '지식 확장', '토론 주제']
    }
    
    return fallback_map.get(genre, ['새로운 관점', '배움과 성장', '경험 공유', '생각의 확장', '의미 찾기'])

# Routes
@app.route('/')
def index():
    members = Member.query.all()
    return render_template('index.html', members=members)

@app.route('/add_book', methods=['POST'])
def add_book():
    try:
        # Get form data
        book_data = {
            'member_name': request.form['member_name'],
            'title': request.form['title'],
            'author': request.form['author'],
            'genre': request.form['genre'],
            'completed': request.form.get('completed') == 'on',
            'rating': int(request.form['rating']) if request.form['rating'] else 0,
            'review': request.form['review']
        }
        
        # Add to Notion
        success, message = add_book_to_notion(book_data)
        
        if success:
            flash('책이 성공적으로 기록되었습니다!', 'success')
        else:
            flash(f'Notion 기록 실패: {message}', 'error')
            
    except Exception as e:
        flash(f'오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/add_member', methods=['POST'])
def add_member():
    try:
        name = request.form['name'].strip()
        if name:
            existing_member = Member.query.filter_by(name=name).first()
            if not existing_member:
                new_member = Member(name=name)
                db.session.add(new_member)
                db.session.commit()
                flash(f'회원 "{name}"이 추가되었습니다!', 'success')
            else:
                flash('이미 존재하는 회원입니다.', 'warning')
        else:
            flash('회원 이름을 입력해주세요.', 'error')
    except Exception as e:
        flash(f'회원 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/members')
def members():
    members = Member.query.all()
    return render_template('members.html', members=members)

@app.route('/generate_keywords', methods=['POST'])
def generate_keywords():
    """Generate discussion keywords based on book information"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        author = data.get('author', '').strip()
        genre = data.get('genre', '').strip()
        review = data.get('review', '').strip()
        
        if not title or not genre:
            return jsonify({
                'success': False,
                'error': '책 제목과 장르는 필수입니다.'
            }), 400
        
        # Generate keywords using GPT + Google Books API
        keywords = generate_keywords_with_gpt(title, author, genre, review)
        
        return jsonify({
            'success': True,
            'keywords': keywords,
            'message': f'{len(keywords)}개의 토론 키워드가 생성되었습니다!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'키워드 생성 중 오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add initial members if none exist
        if Member.query.count() == 0:
            initial_members = ['김철수', '이영희', '박민수', '최유진']
            for name in initial_members:
                member = Member(name=name)
                db.session.add(member)
            db.session.commit()
            print("Initial members added to database")

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=os.getenv('FLASK_ENV') == 'development') 