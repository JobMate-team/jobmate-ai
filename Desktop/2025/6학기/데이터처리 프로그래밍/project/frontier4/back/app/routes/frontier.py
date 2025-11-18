from flask import Blueprint, request, jsonify
from app.services.price_service import fetch_price_history
from app.models.quant_model_modules import efficient_frontier

bp = Blueprint("frontier", __name__)

@bp.route("/api/frontier", methods=["POST"])
def get_frontier():
    data = request.get_json()

    codes = data.get("codes")
    start = data.get("start")
    end = data.get("end")

    if not codes or len(codes) < 2:
        return jsonify({"error": "종목 최소 2개 필요"}), 400

    # 가격 수집
    price_dict = {}
    for code in codes:
        df = fetch_price_history(code, start, end)
        if df.empty:
            return jsonify({"error": f"{code} 데이터 없음"}), 400

        price_dict[code] = df["close"].pct_change().dropna().values

    # returns 매트릭스 만들기
    import numpy as np
    min_len = min(len(r) for r in price_dict.values())
    returns = np.array([r[-min_len:] for r in price_dict.values()]).T

    # 프런티어 계산
    frontier = efficient_frontier(returns)

    return jsonify({"frontier": frontier})
