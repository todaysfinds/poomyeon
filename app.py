from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests
import json
from dotenv import load_dotenv

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