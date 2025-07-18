# 📚 독서모임 기록 시스템

Flask 기반의 독서모임 진행과 기록을 도와주는 웹 애플리케이션입니다.

## ✨ 주요 기능

- 🎯 **회원 관리**: 드롭다운으로 회원 선택 및 새 회원 추가
- 📖 **책 정보 기록**: 제목, 저자, 장르, 완독 여부, 별점, 한줄평 입력
- 🔗 **Notion 연동**: 입력된 정보가 자동으로 Notion 데이터베이스에 저장
- 🤖 **AI 키워드 추천**: GPT + Google Books API를 활용한 토론 키워드 자동 생성
- 📱 **반응형 UI**: Tailwind CSS를 활용한 깔끔한 인터페이스

## 🛠 기술 스택

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite (개발) / PostgreSQL (배포)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **AI**: OpenAI GPT API (gpt-3.5-turbo)
- **External APIs**: Notion API, Google Books API
- **Deploy**: Render

## 🚀 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone https://github.com/todaysfinds/poomyeon.git
cd poomyeon
```

### 2. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
cp .env.example .env
```

`.env` 파일을 열어 다음 값들을 설정하세요:
```
SECRET_KEY=your-secret-key-here
NOTION_TOKEN=your-notion-integration-token
NOTION_DATABASE_ID=your-notion-database-id
OPENAI_API_KEY=your-openai-api-key
GOOGLE_BOOKS_API_KEY=your-google-books-api-key
```

### 5. 애플리케이션 실행
```bash
python app.py
```

브라우저에서 `http://localhost:5000`으로 접속하세요.

## 📊 Notion 데이터베이스 설정

### 필수 속성 (Properties)
Notion 데이터베이스에 다음 속성들을 생성해주세요:

| 속성명 | 타입 | 설명 |
|--------|------|------|
| 이름 | Select | 회원 이름 |
| 책 제목 | Title | 책 제목 (메인 타이틀) |
| 저자 | Text | 저자명 |
| 장르 | Select | 책 장르 |
| 완독 여부 | Checkbox | 완독 여부 |
| 별점 | Number | 1-5점 평점 |
| 한줄평 | Text | 간단한 리뷰 |

### Notion API 토큰 발급
1. [Notion Developers](https://developers.notion.com/)에서 새 Integration 생성
2. 생성된 토큰을 `.env` 파일의 `NOTION_TOKEN`에 설정
3. 데이터베이스를 Integration과 공유
4. 데이터베이스 ID를 `.env` 파일의 `NOTION_DATABASE_ID`에 설정

## 🤖 AI 키워드 추천 설정

### OpenAI API 설정
1. [OpenAI Platform](https://platform.openai.com/)에서 계정 생성
2. API Keys 메뉴에서 새 API 키 생성
3. 생성된 키를 `.env` 파일의 `OPENAI_API_KEY`에 설정
4. 사용량에 따른 요금이 발생할 수 있으니 주의하세요

### Google Books API 설정
1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. "APIs & Services" > "Library"에서 "Books API" 활성화
3. "APIs & Services" > "Credentials"에서 API 키 생성
4. 생성된 키를 `.env` 파일의 `GOOGLE_BOOKS_API_KEY`에 설정

### 키워드 추천 기능
- 책 제목과 저자 정보로 Google Books에서 상세 정보 검색
- 검색된 책 설명과 사용자 입력을 바탕으로 GPT가 토론 키워드 생성
- API 오류 시 장르 기반 기본 키워드로 대체
- 키워드는 화면에만 표시되며 Notion에는 저장되지 않음

## 🌐 Render 배포

### 1. Render 계정 준비
- [Render](https://render.com/) 계정 생성
- GitHub 연동

### 2. 환경변수 설정
Render 대시보드에서 다음 환경변수를 설정하세요:
- `SECRET_KEY`: 자동 생성됨
- `FLASK_ENV`: production
- `NOTION_TOKEN`: Notion Integration 토큰
- `NOTION_DATABASE_ID`: Notion 데이터베이스 ID
- `OPENAI_API_KEY`: OpenAI API 키
- `OPENAI_MODEL`: gpt-3.5-turbo (기본값)
- `GOOGLE_BOOKS_API_KEY`: Google Books API 키
- `DATABASE_URL`: 자동 생성됨 (PostgreSQL)

### 3. 배포
- `render.yaml` 파일이 자동으로 배포 설정을 처리합니다
- PostgreSQL 데이터베이스가 자동으로 생성됩니다

## 📁 프로젝트 구조

```
poomyeon/
├── app.py                 # Flask 애플리케이션 메인 파일
├── requirements.txt       # Python 패키지 의존성
├── render.yaml           # Render 배포 설정
├── .env.example          # 환경변수 예시 파일
├── .gitignore            # Git 제외 파일 목록
├── templates/            # HTML 템플릿
│   ├── base.html        # 기본 레이아웃
│   ├── index.html       # 메인 페이지 (책 기록)
│   └── members.html     # 회원 관리 페이지
└── static/              # 정적 파일 (현재 비어있음)
```

## 🔧 개발 정보

### 데이터베이스 모델
- `Member`: 회원 정보 (이름, 가입일)

### API 엔드포인트
- `GET /`: 메인 페이지 (책 기록 폼)
- `POST /add_book`: 새 책 기록 추가
- `GET /members`: 회원 관리 페이지
- `POST /add_member`: 새 회원 추가
- `GET /health`: 헬스체크

## 📝 TODO

- [ ] 장르별 질문 키워드 시스템 구현
- [ ] 책 기록 목록 보기 기능
- [ ] 회원별 통계 기능
- [ ] 책 기록 수정/삭제 기능

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 있습니다.

## 📞 연락처

GitHub: [@todaysfinds](https://github.com/todaysfinds)
Project Link: [https://github.com/todaysfinds/poomyeon](https://github.com/todaysfinds/poomyeon) 