import requests
import json
# url = "http://127.0.0.1:8001/ai-feedback"
# payload = {
#     "job_group": "백엔드",
#     "job": "Python 백엔드 개발자",
#     "company": "네이버",
#     "question": "최근에 어려웠던 기술적 문제를 해결한 경험을 말씀해 주세요.",
#     "answer": "API 응답 속도가 느린 문제를 겪었습니다. DB 쿼리 최적화와 캐싱을 도입해서 50%의 응답시간을 개선했습니다.",
#     "standard_question": "n",  
#     "question_id": "IT-R&D-001"        
# }

jp = input("직군을 입력하세요 (예: IT, 마케팅, 디자인 등): ")
q = input("질문 키워드를 입력하세요 (예: OSI, 마케팅 전략 등): ")
a = input("답변 내용을 입력하세요: ")
k = int(input("가져올 도큐먼트 개수를 입력하세요 (예: 3): "))


url = "http://localhost:8000/structured-feedback"
payload = {
    "job_family": jp,      # 예: "tech"
    "question": q,
    "answer": a,
    "top_k": k                # 가져올 도큐먼트 개수
}

# # --- /random-questions 예시 페이로드 ---
# url = "http://127.0.0.1:8001/random-questions"
# payload = {
#     "q_list": ["tech"],
#     "count": 1
# }
response = requests.post(url, json=payload)
print(json.dumps(response.json(), ensure_ascii=False, indent=2))