# 하나펀드 서비스

## 프로젝트 구조
- `web/`: PHP 웹 프론트엔드 파일
- `src/`: Python 백엔드 소스 코드
- `config/`: 설정 파일
- `docker/`: Docker 관련 설정 파일
- `main.py`: Python 애플리케이션 진입점 및 PHP 연동 서버

## 설치 및 실행 방법

### 필수 요구사항
- Docker
- Docker Compose

### 실행 방법
1. 저장소 클론
```bash
git clone <repository-url>
cd Hanafund
```

2. Docker Compose로 서비스 실행
```bash
docker-compose up -d
```

3. 웹 브라우저에서 접속
```
http://localhost:8000
```

## 서비스 구성
- **통합 애플리케이션**: Python 백엔드와 PHP 프론트엔드가 하나의 컨테이너에서 실행
- **Python 기능**: OCR 및 데이터 처리 서비스
- **PHP 프론트엔드**: 사용자 인터페이스 제공

## 볼륨 정보
- `php_logs`: PHP-FPM 로그 저장
- `python_data`: Python 서비스 데이터 저장
- `logs`: 애플리케이션 로그 저장