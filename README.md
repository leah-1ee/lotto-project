# 🎱 Lotto 6/45 Web Service

Django + Docker 기반 로또 6/45 웹 서비스입니다.

---

## 📌 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프레임워크 | Django 4.2.7 |
| 데이터베이스 | PostgreSQL 15 |
| 웹 서버 | Nginx (Alpine) |
| WSGI 서버 | Gunicorn 21.2.0 |
| 컨테이너 | Docker (멀티컨테이너) |

---

## ✨ 주요 기능

### 일반 사용자
- 회원가입 / 로그인 / 로그아웃
- 복권 **수동 구매** (번호판 UI에서 1~45 중 6개 직접 선택)
- 복권 **자동 구매** (시스템이 무작위 6개 선택)
- 내 복권 목록 조회
- 당첨 결과 확인 (등수 및 당첨번호 비교)

### 관리자
- 관리자 대시보드 (판매 수, 회차 통계)
- 회차 생성 및 추첨 실행
- 전체 판매 내역 조회
- 전체 당첨 내역 조회

---

## 🏗 시스템 아키텍처

```
[ 사용자 브라우저 ]
        | :80
        v
[ Nginx 컨테이너  ]  ← 정적 파일 서빙 + 리버스 프록시
        | :8000
        v
[ Django 컨테이너 ]  ← 웹 애플리케이션 (Gunicorn)
        | :5432
        v
[ PostgreSQL 컨테이너 ] ← 데이터베이스
```

---

## 📁 프로젝트 구조

```
lotto-project/
├── .env                      # 환경변수 (Git 제외)
├── .gitignore
├── docker-compose.yml
├── django/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   └── urls.py
│   └── lotto/
│       ├── models.py         # Draw, Ticket, WinResult
│       ├── views.py
│       ├── forms.py
│       ├── urls.py
│       └── templates/lotto/  # HTML 템플릿 11개
└── nginx/
    └── nginx.conf
```

---

## 🚀 실행 방법

### 1. 저장소 클론

```bash
git clone https://github.com/YOUR_USERNAME/lotto-project.git
cd lotto-project
```

### 2. 환경변수 파일 생성

```bash
cat > .env << EOF
DB_NAME=lottodb
DB_USER=lottouser
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your-secret-key
DEBUG=True
EOF
```

### 3. 컨테이너 빌드 및 실행

```bash
docker compose up --build -d
```

### 4. DB 마이그레이션 및 관리자 계정 생성

```bash
docker compose exec web python manage.py makemigrations lotto
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 5. 브라우저 접속

```
http://localhost
```

---

## 🗄 데이터베이스 모델

| 모델 | 설명 |
|------|------|
| User | Django 기본 모델. is_staff로 관리자 구분 |
| Draw | 회차 정보 및 당첨번호 저장 |
| Ticket | 구매한 복권 정보 (수동/자동) |
| WinResult | 추첨 후 생성되는 당첨 결과 |

### 당첨 등수 기준

| 등수 | 조건 |
|------|------|
| 1등 | 6개 번호 모두 일치 |
| 2등 | 5개 일치 + 보너스 번호 일치 |
| 3등 | 5개 번호 일치 |
| 4등 | 4개 번호 일치 (50,000원) |
| 5등 | 3개 번호 일치 (5,000원) |
| 낙첨 | 2개 이하 일치 |

---

## 🐳 Docker 컨테이너 구성

| 컨테이너 | 이미지 | 포트 |
|----------|--------|------|
| lotto_db | postgres:15 | 5432 |
| lotto_web | python:3.11-slim (커스텀) | 8000 |
| lotto_nginx | nginx:alpine | 80 |

---

## 🔑 주요 URL

| URL | 설명 | 대상 |
|-----|------|------|
| `/` | 메인 페이지 | 전체 |
| `/register/` | 회원가입 | 전체 |
| `/login/` | 로그인 | 전체 |
| `/buy/` | 복권 구매 | 일반 사용자 |
| `/my-tickets/` | 내 복권 목록 | 일반 사용자 |
| `/check-win/` | 당첨 확인 | 일반 사용자 |
| `/admin-dashboard/` | 관리자 대시보드 | 관리자 |
| `/admin-draw/` | 추첨 관리 | 관리자 |
| `/admin-sales/` | 판매 내역 | 관리자 |
| `/admin-results/` | 당첨 내역 | 관리자 |
| `/django-admin/` | Django 기본 관리자 | 관리자 |

---

## ⚠️ 주의사항

- `.env` 파일은 보안상 Git에 포함되지 않습니다. 직접 생성이 필요합니다.
- `DEBUG=True`는 개발 환경 전용입니다. 운영 환경에서는 반드시 `False`로 변경하세요.
- `SECRET_KEY`는 운영 환경에서 반드시 새로운 값으로 교체하세요.