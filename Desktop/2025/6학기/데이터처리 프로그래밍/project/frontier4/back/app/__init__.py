import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    load_dotenv() 
    
    print("--- ★★★ app/__init__.py 의 create_app()이 호출되었습니다. ★★★ ---")
    
    app = Flask(__name__)
    CORS(app)

    # 🌟 기본 routes
    from . import routes
    app.register_blueprint(routes.bp)

    # 🌟 효율적 프론티어 + 최적화 API
    from app.api.optimize_api import optimize_api
    app.register_blueprint(optimize_api)

    # 🌟 🔥 AI 챗봇 API 추가 
    from app.ai_chat import bp_ai
    app.register_blueprint(bp_ai)

    return app

