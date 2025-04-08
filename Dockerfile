# Python 베이스 이미지 사용
FROM python:3.11-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 생성
WORKDIR /code

# 시스템 의존성 설치
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt-get clean

# requirements 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 소스 복사
COPY . .

# 포트 설정 (장고 dev 서버용)
EXPOSE 8000
# 기존 runserver 대신 gunicorn 실행
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "my_first_blog.wsgi:application"]
