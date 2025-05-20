#!/bin/bash
set -e

# 웹 디렉토리 권한 설정
chown -R www-data:www-data /hanafund/web
chmod -R 755 /hanafund/web

# PHP 파일을 공유 볼륨으로 복사
echo "웹 파일을 공유 볼륨으로 복사합니다..."
cp -rf /hanafund/web/* /var/www/html/
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html

# 로그 디렉토리 생성 및 권한 설정
mkdir -p /var/log/php-fpm /hanafund/logs
chown -R www-data:www-data /var/log/php-fpm
chown -R www-data:www-data /hanafund/logs

# FPM 소켓 디렉토리 권한 설정
mkdir -p /var/run/php
chown -R www-data:www-data /var/run/php

echo "PHP-FPM이 0.0.0.0:9000에서 수신 대기 중입니다."
echo "모든 준비가 완료되었습니다."

# PHP-FPM, Python 등 서비스 시작은 Supervisor가 담당
exec "$@" 