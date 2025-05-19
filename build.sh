#!/bin/bash
set -e

IMAGE_NAME="hanafund_ocr:poc"
CONTAINER_NAME="hanafund_ocr_poc"
NETWORK_NAME="YOUR Network name"    
HOST_DIR="$(pwd)"
CONTAINER_DIR="/hanafund_ocr"

echo "[1/3] DOCKER_BUILDKIT 활성화 및 빌드 시작..."
DOCKER_BUILDKIT=1 docker-compose build

echo "[2/3] 빌드 완료 — 이미지 확인:"
docker images | grep $IMAGE_NAME || echo "이미지 없음: $IMAGE_NAME"

echo "[3/3] 컨테이너 실행 중..."
docker run -it \
  -v "$HOST_DIR:$CONTAINER_DIR" \
  -p 8081:8081 \
  --name "$CONTAINER_NAME" \
  --network "$NETWORK_NAME" \
  "$IMAGE_NAME" bash