import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# .env 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env를 확인하세요.")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_ai_project")

# OpenAI 클라이언트 및 임베딩 (싱글톤처럼 사용)
client = OpenAI(api_key=OPENAI_API_KEY)
embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
DATA_DIR = os.path.join(BASE_DIR, "src", "embedding")

# 디버깅용 출력 (서버 켤 때 경로가 맞는지 확인용)
print(f"✅ 설정된 DATA_DIR 경로: {DATA_DIR}")

if not os.path.exists(DATA_DIR):
    logger.error(f"❌ DATA_DIR 경로가 존재하지 않습니다: {DATA_DIR}")

FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")