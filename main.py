import os
import sys
import logging
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# PHP 웹 파일 경로 설정
WEB_PATH = os.environ.get("PHP_WEB_PATH", "./web")

def main():
    """
    메인 애플리케이션 진입점
    """
    logger.info("하나펀드 서비스가 시작되었습니다.")
    logger.info(f"PHP 웹 경로: {WEB_PATH}")
    logger.info("PHP-FPM이 9000 포트에서 실행 중입니다.")
    logger.info("외부 Nginx에서 이 컨테이너로 PHP 요청을 전달합니다.")
    
    # 추가적인 초기화 작업이 필요하면 여기에 추가
    
    # 컨테이너가 종료되지 않도록 무한 루프로 유지
    try:
        while True:
            time.sleep(60)
            logger.debug("애플리케이션 실행 중...")
    except KeyboardInterrupt:
        logger.info("애플리케이션이 종료됩니다.")
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        raise

if __name__ == "__main__":
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # 메인 애플리케이션 실행
    main() 