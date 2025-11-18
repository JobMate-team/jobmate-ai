def calculate_weights(payload):
    # TODO: 실제 가중치 계산 로직으로 교체
    # 임시: 자산 개수만큼 균등 가중치
    assets = payload.get("assets", [])
    n = len(assets) or 1
    w = [1.0 / n] * n
    return {"weights": {assets[i]["symbol"]: w[i] for i in range(len(assets))}}
