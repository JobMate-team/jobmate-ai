# app/ai_chat.py
import os
from flask import Blueprint, request, jsonify, abort
import google.generativeai as genai

bp_ai = Blueprint("ai_chat", __name__)

# Gemini 모델 초기화
api_key = os.getenv("GEMINI_API_KEY")
gemini_model = None

if api_key:
    try:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            system_instruction="당신은 전문적인 AI 자산배분 분석 도우미입니다."
        )
        print("✅ Gemini 모델 초기화 성공 (ai_chat.py)")
    except Exception as e:
        print(f"🚨 Gemini 모델 초기화 실패: {e}")
else:
    print("🚨 GEMINI_API_KEY 없음. .env 파일 확인 필요.")


# /chat 엔드포인트
@bp_ai.post("/chat")
def handle_chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        abort(400, "message is required")

    if not gemini_model:
        abort(503, "AI service not available")

    try:
        response = gemini_model.generate_content(user_message)
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"AI error: {e}")
        abort(500, "Error processing AI response")
