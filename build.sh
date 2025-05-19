#!/bin/bash
set -e
IMAGE_NAME="hanafund_ocr_final"

echo "[1/3] DOCKER_BUILDKIT 활성화 및 빌드 시작..."
DOCKER_BUILDKIT=1 docker-compose build

echo "[2/3] 빌드 완료 — 이미지 확인:"
docker images | grep $IMAGE_NAME || echo "이미지 없음: $IMAGE_NAME"

echo "[3/3] 컨테이너 실행 중..."
docker-compose up -d

echo "완료! 현재 실행 중인 컨테이너:"
docker ps --filter "ancestor=$IMAGE_NAME"