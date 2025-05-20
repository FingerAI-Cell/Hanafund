# Dockerfile for Hanafund OCR with PHP support
# write by Jaedong, Oh (2025.05.13)
# Updated by Cursor Assistant (2025.05.19)
# --- Builder stage ---
FROM python:3.12-slim-bullseye AS builder
WORKDIR /app

# 필수 도구만 설치
RUN apt-get update && apt-get install -y --no-install-recommends python3-venv build-essential git locales && \
    python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .

# 필요 패키지 설치
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt 

# --- Inference image ---
FROM python:3.12-slim-bullseye
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /hanafund_ocr

# PHP 저장소 추가 및 PHP와 PHP-FPM 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    lsb-release \
    wget \
    gnupg \
    supervisor \
    && wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg \
    && echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    php8.1 \
    php8.1-fpm \
    php8.1-common \
    php8.1-cli \
    php8.1-cgi \
    php8.1-mysql \
    php8.1-curl \
    php8.1-mbstring \
    php8.1-xml \
    php8.1-zip \
    php8.1-gd \
    libonig-dev \
    libxml2-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# PHP-FPM 설정 파일 복사
COPY ./docker/php/www.conf /etc/php/8.1/fpm/pool.d/www.conf
COPY ./docker/php/php.ini /etc/php/8.1/fpm/php.ini

# Supervisor 설정 파일 복사
COPY ./docker/supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 웹 콘텐츠 권한 설정
RUN mkdir -p /var/log/php-fpm /var/run/php /hanafund/logs /hanafund/web \
    && chown -R www-data:www-data /var/log/php-fpm \
    && chown -R www-data:www-data /var/run/php \
    && chown -R www-data:www-data /hanafund/logs \
    && chown -R www-data:www-data /hanafund/web \
    && chmod -R 755 /hanafund/web

# 엔트리포인트 스크립트 복사
COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Python 기능 복사
COPY --from=builder /opt/venv /opt/venv
COPY . .

# 포트 노출
EXPOSE 9000

# 엔트리포인트 실행
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]