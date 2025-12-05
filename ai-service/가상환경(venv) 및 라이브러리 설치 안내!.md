가상환경(venv) 및 라이브러리 설치 안내!



① 폴더이동 

cd C:\\Users\\...\\jobmate-ai\\ai-service\\src

② venv 생성( src 폴더에 이미 생성되어 있으니 패스해도 됨) 

python -m venv venv

③ venv 활성화( 앞에 venv 붙으면 됨)

.\\venv\\Scripts\\activate

④ 라이브러리 설치

pip install -r requirements.txt



실행 방법 안내!

① .env 파일 ( openai api key 제가 카톡방에 보내드리겠습니다!)

② embedding/ 폴더 안에 json 4개 (cli\_main.py는 지수님 코드 입니다!)

&nbsp;ai-service/

&nbsp; main.py

&nbsp; .env

&nbsp; embedding/

&nbsp;   question\_templates.json

&nbsp;   answer\_patterns.json

&nbsp;   competency\_rubrics.json

&nbsp;   model\_answers.json

③ 서버 실행

(venv) uvicorn main:app --reload --port 8001

④ 브라우저에서 테스트

주소: http://127.0.0.1:8001/docs

POST /ai-feedback → Try it out

request body 예시:

{

&nbsp; "job": "백엔드 개발자",

&nbsp; "company": "카카오",

&nbsp; "question": "최근에 경험한 프로젝트 중에서 가장 인상 깊었던 경험을 말해 주세요.",

&nbsp; "answer": "대학교 팀프로젝트에서 쇼핑몰 웹서비스의 백엔드 개발을 맡았습니다. 처음에는 단순 CRUD 위주로 구현했지만, 트래픽이 늘면서 응답 속도가 느려지는 문제가 발생했습니다. 저는 로그와 APM을 분석해 병목 API를 찾았고, 쿼리 리팩터링과 캐시를 도입해 평균 응답 시간을 약 40% 줄였습니다."

}

이후 답변 확인 가능합니다!



