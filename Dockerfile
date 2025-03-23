FROM python:3.11-slim-buster

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt update && apt install -y \
    gcc \
    python3-dev \
    libffi-dev \
    libpq-dev \
    cargo \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사
COPY requirements.txt /app/

# pip 업그레이드 및 패키지 설치
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 애플리케이션 코드 복사
COPY . /app/

# 기본 실행 명령어
CMD ["python", "app.py"]
