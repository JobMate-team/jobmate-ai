from fastapi import FastAPI
from src.routers import feedback, search
from src.services.rag_service import init_vectorstore

app = FastAPI()

# 라우터 등록
app.include_router(search.router)
app.include_router(feedback.router)

@app.on_event("startup")
async def startup_event():
    # 앱 시작 시 벡터 DB 로드 (지연 시간 방지)
    print("앱 시작: 벡터 스토어 초기화 중...")
    init_vectorstore()
    print("벡터 스토어 준비 완료.")

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # 로컬 테스트용
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)