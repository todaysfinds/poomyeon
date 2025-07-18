# 📚 독서모임 기록 시스템

Flask 기반의 독서모임 진행과 기록을 도와주는 웹 애플리케이션입니다.

## ✨ 주요 기능

- 🎯 **회원 관리**: 드롭다운으로 회원 선택 및 새 회원 추가
- 📖 **책 정보 기록**: 제목, 저자, 장르, 완독 여부, 별점, 한줄평 입력
- 🔗 **Notion 연동**: 입력된 정보가 자동으로 Notion 데이터베이스에 저장
- 📱 **반응형 UI**: Tailwind CSS를 활용한 깔끔한 인터페이스

## 🛠 기술 스택

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite (개발) / PostgreSQL (배포)
- **Frontend**: HTML, Tailwind CSS
- **API**: Notion API
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