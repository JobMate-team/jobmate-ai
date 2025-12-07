### 가상환경(venv) 및 라이브러리 설치 안내!

① 폴더이동
```

cd C:\Users\...\jobmate-ai

```


② 가상환경 (venv) 생성

```python -m venv {your venv}```

③ venv 활성화( 앞에 venv 붙으면 됨)

```
[Window]
.\{yourvenv}\Scripts\activate
[Mac]
source {your venv}/bin/activate

```

④ 라이브러리 설치

```pip install -r requirements.txt```

실행 방법 안내!

① .env 파일

② embedding/ 폴더 안에 json 4개

 jobmate-ai/

  main.py

  .env

  embedding/

  question_templates.json

  answer_patterns.json

  competency_rubrics.json

  model_answers.json

③ 서버 실행
```
(venv) uvicorn main:app --reload --port 8001

```

④ 브라우저에서 테스트


http://127.0.0.1:8001/docs


POST /ai-feedback → Try it out

request body 예시:
```
{

  "job_group": "IT",

  "job": "소프트웨어개발자",

  "company": "삼성전자",

  "question": "최근에 경험한 프로젝트 중에서 가장 인상 깊었던 경험을 말해 주세요.",

  "answer": "네, 4인 팀으로 진행했던 졸업 프로젝트에서 한 팀원이 개인 사정을 이유로 맡은 파트의 진행이 계속 늦어졌던 경험이 있습니다. (Situation) 마감 기한은 다가오는데 핵심 기능 구현이 지연되면서 프로젝트 전체에 차질이 생길 수 있는 위기 상황이었습니다. (Task) 저는 프로젝트를 성공적으로 완수하기 위해 이 문제를 해결해야 한다고 생각했습니다. 단순히 그 팀원을 비난하기보다는, 함께 해결책을 찾는 것이 중요하다고 판단했습니다. (Action) 먼저, 그 팀원과 따로 만나 이야기를 나누며 어려움을 들어주었습니다. 알고 보니, 해당 파트에 대한 기술적 이해도가 부족해 어디서부터 시작해야 할지 막막함을 느끼고 있었습니다. 그래서 저는 제가 먼저 관련 기술 자료를 리서치하여 정리해주고, 매일 30분씩 '페어 프로그래밍'을 하자고 제안했습니다. 함께 코드를 보며 막히는 부분을 같이 해결하고, 제가 아는 부분을 설명해주며 진행을 도왔습니다. (Result) 그 결과, 팀원은 다시 의욕을 되찾아 본인의 역할을 완수할 수 있었고, 저희 팀은 프로젝트를 성공적으로 마감하여 우수한 성적을 거둘 수 있었습니다. 이 경험을 통해 동료의 어려움에 공감하고 실질적인 도움을 통해 함께 문제를 해결하는 협업의 중요성을 배울 수 있었습니다."

}
```
