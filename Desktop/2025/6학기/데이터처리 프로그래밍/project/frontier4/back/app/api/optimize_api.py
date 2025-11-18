from flask import Blueprint, request, jsonify
from app.services.return_service import build_returns_dataframe
from app.services.optimization_service import (
    compute_efficient_frontier,
    optimize_for_risk
)

# Blueprint 생성
optimize_api = Blueprint("optimize_api", __name__, url_prefix="/api/optimize")


# -------------------------------------------
# 🔥 1) Efficient Frontier API
# -------------------------------------------
@optimize_api.route("/frontier", methods=["POST"])
def efficient_frontier_api():
    try:
        data = request.get_json()
        codes = data.get("codes", [])
        start = data.get("start")
        end = data.get("end")

        if not codes or len(codes) < 2:
            return jsonify({"error": "2개 이상의 종목 필요"}), 400

        # 수익률 데이터 생성
        df_returns = build_returns_dataframe(codes, start, end)

        if df_returns.empty:
            return jsonify({"error": "수익률 데이터 없음"}), 400

        # 프론티어 계산
        risks, returns_, weights = compute_efficient_frontier(df_returns)

        # numpy 타입 → float
        risks = [float(r) for r in risks]
        returns_ = [float(r) for r in returns_]
        weights = [[float(w) for w in row] for row in weights]

        return jsonify({
            "risks": risks,
            "returns": returns_,
            "weights": weights
        })

    except Exception as e:
        print("🔥 Efficient Frontier ERROR:", e)
        return jsonify({"error": str(e)}), 500



# -------------------------------------------
# 🔥 2) Risk-based Optimization API
# -------------------------------------------
@optimize_api.route("/risk", methods=["POST"])
def optimize_by_risk():
    try:
        data = request.get_json()
        codes = data["codes"]
        risk_level = data["risk_level"]  # 0~1
        start = data.get("start")
        end = data.get("end")

        df_returns = build_returns_dataframe(codes, start, end)

        weights, vol, ret = optimize_for_risk(df_returns, risk_level)

        return jsonify({
            "weights": [float(w) for w in weights],
            "risk": float(vol),
            "expected_return": float(ret)
        })

    except Exception as e:
        print("🔥 Risk Optimization ERROR:", e)
        return jsonify({"error": str(e)}), 500
