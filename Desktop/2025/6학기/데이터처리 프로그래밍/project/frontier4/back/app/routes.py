# app/routes.py

import logging
logging.basicConfig(level=logging.DEBUG)
import os
import json
import requests
from flask import request, jsonify, Blueprint

# ===== 주식정보 관련 서비스 =====
from .services.stock_service import get_stock_info
from .services.price_service import fetch_price_history
from .services.return_service import build_returns_dataframe

# ===== 포트폴리오 최적화 모델 =====
from models.quant_model_modules import (
    compute_min_variance,
    compute_max_sharpe,
    compute_risk_parity,        
    compute_max_diversification,
    compute_target_risk,        
    compute_efficient_frontier  
)

bp = Blueprint("routes", __name__)

# ============================================================
# 0. 종목 DB 로딩
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STOCKS_PATH = os.path.join(DATA_DIR, "stocks.json")

STOCKS: list[dict] = []

try:
    with open(STOCKS_PATH, "r", encoding="utf-8") as f:
        STOCKS = json.load(f)
except Exception as e:
    print(f"[WARN] Failed to load stocks.json: {e}")
    STOCKS = []


def resolve_code(query: str) -> str:
    if not query:
        return query

    q = str(query).strip()

    if q.isdigit() and len(q) == 6:
        return q

    norm_q = q.replace(" ", "")
    for item in STOCKS:
        if item.get("name", "").replace(" ", "") == norm_q:
            return item.get("code", "")

    return q


# ============================================================
# 1. Health Check
# ============================================================
@bp.route("/api/health")
def health():
    return jsonify({"status": "ok"})


# ============================================================
# 2. 개별 종목 조회
# ============================================================
@bp.route("/api/stock", methods=["GET"])
def get_stock():
    raw = (
        request.args.get("query")
        or request.args.get("code")
        or request.args.get("q")
    )

    if not raw:
        return jsonify({"error": "query 또는 code 필요"}), 400

    code = resolve_code(raw)

    if not (code.isdigit() and len(code) == 6):
        return jsonify({"error": f"'{raw}'에 해당하는 코드를 찾을 수 없습니다."}), 404

    try:
        stock = get_stock_info(code)
    except Exception as e:
        return jsonify({"error": "서버 오류", "detail": str(e)}), 500

    if not stock:
        return jsonify({"error": "종목 정보 없음"}), 404

    return jsonify(stock)


# ============================================================
# 3. 네이버 뉴스 검색
# ============================================================
@bp.route("/api/search-news", methods=["GET"])
def search_news():
    query = (
        request.args.get("query")
        or request.args.get("q")
        or request.args.get("code")
        or ""
    ).strip()

    if not query:
        return jsonify({"error": "query 필요"}), 400

    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return jsonify({"error": "네이버 API 키 없음"}), 500

    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": 10, "sort": "date"}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        res.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"네이버 API 오류: {e}"}), 502

    return jsonify(res.json())


# ============================================================
# 4. 가격 히스토리
# ============================================================
@bp.route("/api/price-history", methods=["GET"])
def api_price_history():
    code = request.args.get("code", "").strip()
    start = request.args.get("start")
    end = request.args.get("end")

    if not code:
        return jsonify({"error": "code 필요"}), 400

    try:
        df = fetch_price_history(code, start, end)
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": "데이터 수집 실패", "detail": str(e)}), 500


# ============================================================
# 5. 수익률 계산
# ============================================================
@bp.route("/api/returns", methods=["POST"])
def api_returns():
    data = request.get_json()
    codes = data.get("codes")
    start = data.get("start")
    end = data.get("end")

    if not codes:
        return jsonify({"error": "codes 필요"}), 400

    try:
        df = build_returns_dataframe(codes, start, end)
        return jsonify(df.reset_index().to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": "수익률 계산 실패", "detail": str(e)}), 500


# ============================================================
# 6. 최적화 공통 래퍼
# ============================================================
def optimize_wrapper(optimizer, codes, start, end):
    try:
        df = build_returns_dataframe(codes, start, end)
        return optimizer(df)
    except Exception as e:
        return {"error": "최적화 실패", "detail": str(e)}


def unpack_result(result):
    if isinstance(result, dict) and result.get("error"):
        return None, None, None, result

    if isinstance(result, (tuple, list)):
        if len(result) == 3:
            return result[0], result[1], result[2], None
        if len(result) == 2:
            return result[0], result[1], None, None
        if len(result) == 1:
            return result[0], None, None, None

    return None, None, None, {"error": "Invalid return format"}


# ============================================================
# 6-1. 최소 분산
# ============================================================
@bp.route("/api/optimize/min-variance", methods=["POST"])
def api_min_variance():
    data = request.get_json()
    result = optimize_wrapper(
        compute_min_variance, data.get("codes"), data.get("start"), data.get("end")
    )
    weights, risk, exp_ret, error = unpack_result(result)

    if error:
        return jsonify(error), 500

    return jsonify({
        "weights": weights.tolist(),
        "risk": float(risk),
        "expected_return": float(exp_ret),
    })


# ============================================================
# 6-2. 최대 샤프
# ============================================================
@bp.route("/api/optimize/max-sharpe", methods=["POST"])
def api_max_sharpe():
    data = request.get_json()
    result = optimize_wrapper(
        compute_max_sharpe, data.get("codes"), data.get("start"), data.get("end")
    )
    weights, risk, exp_ret, error = unpack_result(result)

    if error:
        return jsonify(error), 500

    return jsonify({
        "weights": weights.tolist(),
        "risk": float(risk),
        "expected_return": float(exp_ret),
    })


# ============================================================
# 6-3. 리스크 패리티
# ============================================================
@bp.route("/api/optimize/risk-parity", methods=["POST"])
def api_risk_parity():
    import sys

    data = request.get_json()
    codes = data.get("codes")
    start = data.get("start")
    end = data.get("end")

    if not codes:
        return jsonify({"error": "codes 필요"}), 400

    try:
        df = build_returns_dataframe(codes, start, end)

        if df.empty:
            return jsonify({"error": "수익률 데이터가 비어 있습니다."}), 400

        print("\n===== [RISK PARITY] Returns DF.tail() =====", flush=True)
        print(df.tail(), flush=True)

        # ===== 실제 계산 =====
        weights, risk, expected_return = compute_risk_parity(df)

        print("[RISK PARITY] result:", weights, risk, expected_return, flush=True)

        return jsonify(
            {
                "weights": weights.tolist(),
                "risk": float(risk),
                "expected_return": float(expected_return),
            }
        )

    except Exception as e:
        import traceback
        print("\n🔥 [RISK-PARITY ERROR] === Traceback ===", flush=True)
        traceback.print_exc()
        sys.stdout.flush()
        return jsonify({"error": "리스크 패리티 실패", "detail": str(e)}), 500


# ============================================================
# 6-4. 최대 분산비율
# ============================================================
@bp.route("/api/optimize/max-diversification", methods=["POST"])
def api_max_div():
    data = request.get_json()
    result = optimize_wrapper(
        compute_max_diversification, data.get("codes"), data.get("start"), data.get("end")
    )
    weights, risk, exp_ret, error = unpack_result(result)

    if error:
        return jsonify(error), 500

    return jsonify({
        "weights": weights.tolist(),
        "risk": float(risk),
        "expected_return": float(exp_ret),
    })


# ============================================================
# 6-5. 효율적 프론티어 (그래프 데이터)
# ============================================================
@bp.route("/api/optimize/frontier", methods=["POST"])
def api_efficient_frontier():
    try:
        data = request.get_json()
        codes = data.get("codes")
        start = data.get("start")
        end = data.get("end")

        if not codes or len(codes) < 2:
            return jsonify({"error": "2개 이상의 종목 필요"}), 400

        # 수익률 DF 생성
        df = build_returns_dataframe(codes, start, end)

        print("\n=== [FRONTIER] df.head() ===")
        print(df.head())

        if df.empty:
            return jsonify({"error": "수익률 데이터가 비어있습니다."}), 400

        # 효율적 프론티어 계산
        risks, returns, weights = compute_efficient_frontier(df)

        return jsonify({
            "risks": risks,
            "returns": returns,
            "weights": weights
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "efficient frontier 실패", "detail": str(e)}), 500





# ============================================================
# 6-5. 목표 리스크(target-risk) 최적화
# ============================================================
@bp.route("/api/optimize/target-risk", methods=["POST"])
def api_target_risk():
    try:
        data = request.get_json()

        codes = data.get("codes")
        start = data.get("start")
        end = data.get("end")
        target_ratio = data.get("target_risk")  # 0~1

        if not codes or target_ratio is None:
            return jsonify({"error": "codes와 target_risk 필요"}), 400

        df = build_returns_dataframe(codes, start, end)
        if df.empty:
            return jsonify({"error": "수익률 데이터 없음"}), 400

        # 🔥 핵심: target_ratio 변환
        target_ratio = float(target_ratio)
        if target_ratio > 1:
            target_ratio /= 100

        weights, risk, expected_return = compute_target_risk(df, target_ratio)

        return jsonify(
            {
                "weights": weights.tolist(),
                "risk": float(risk),
                "expected_return": float(expected_return),
            }
        )

    except Exception as e:
        print("[TARGET-RISK ERROR]", e)
        return jsonify({"error": str(e)}), 500




# ============================================================
# 🔥 통합 모델 최적화 API
# ============================================================
@bp.route("/api/optimize/model", methods=["POST"])
def api_optimize_model():
    data = request.get_json()

    model = data.get("model")
    codes = data.get("codes")
    start = data.get("start")
    end = data.get("end")

    if not model or not codes:
        return jsonify({"error": "model과 codes 필수"}), 400

    # 🔥 target_risk 입력 통합 처리
    raw_ratio = (
        data.get("target_risk")
        or data.get("risk")
        or data.get("riskLevel")
        or data.get("risk_level")
    )

    # 기본값
    if raw_ratio is None:
        target_ratio = 0.5
    else:
        target_ratio = float(raw_ratio)
        if target_ratio > 1:
            target_ratio = target_ratio / 100.0

    # 수익률 생성
    try:
        df = build_returns_dataframe(codes, start, end)
    except Exception as e:
        return jsonify({"error": "수익률 생성 실패", "detail": str(e)}), 500

    # 최적화 실행
    try:
        if model == "min-variance":
            w, risk, exp_ret = compute_min_variance(df)

        elif model == "max-sharpe":
            w, risk, exp_ret = compute_max_sharpe(df)

        elif model == "risk-parity":
            w, risk, exp_ret = compute_risk_parity(df)

        elif model == "max-div":
            w, risk, exp_ret = compute_max_diversification(df)

        elif model == "target-risk":
            w, risk, exp_ret = compute_target_risk(df, target_ratio)

        else:
            return jsonify({"error": f"알 수 없는 모델: {model}"}), 400

        return jsonify({
            "weights": list(w),
            "risk": float(risk),
            "expected_return": float(exp_ret)
        })

    except Exception as e:
        return jsonify({"error": "최적화 중 오류", "detail": str(e)}), 500

