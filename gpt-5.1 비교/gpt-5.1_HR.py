#######/random-questions

{
  "job_family": "HR",
  "q_list": ["experience", "tenacity", "behavioral"],
  "count": 2
}

{
  "groups": [
    {
      "question_type": "tenacity",
      "questions": [
        {
          "page_text": "도전 경험과 성취 경험",
          "metadata": {
            "question_id": "HR-HRManager-011",
            "question_type": "tenacity",
            "competency_tags": [
              "resilience",
              "problem_solving"
            ],
            "difficulty": 3,
            "job_family": "HR",
            "position": "HR 매니저 (인사 관리자)",
            "level": "신입",
            "source": "잡코리아-롯데그룹",
            "feature": "question",
            "question_text": [
              "본인의 도전경험을 말해보세요.",
              "다른사람에게 칭찬받았던 경험은 무엇인가요?",
              "남들이 다 어려워하는것을 본인이 쉽게 해설해서 분석했던 경험은?",
              "어려운 과제를 스스로 도전하여 성과를 냈던 사례가 있다면 알려 주세요."
            ]
          }
        }
      ]
    },
    {
      "question_type": "job",
      "questions": [
        {
          "page_text": "근무지 희망과 울산 사업장 인사관리",
          "metadata": {
            "question_id": "HR-HRManager-013",
            "question_type": "job",
            "competency_tags": [
              "motivation",
              "company_fit"
            ],
            "difficulty": 3,
            "job_family": "HR",
            "position": "HR 매니저 (인사 관리자)",
            "level": "신입",
            "source": "잡코리아-롯데그룹",
            "feature": "question",
            "question_text": [
              "근무지를 울산공장으로 희망하였는데 이유가 무엇인가요?",
              "글로벌 사업관리 방향에 대해 울산 사업장에서 어떠한 인사관리를 해야 된다고 생각하시나요?",
              "특정 지역 사업장에서 근무하는 것에 대해 어떤 기대와 각오를 가지고 있는지 말해 주세요."
            ]
          }
        }
      ]
    },
    {
      "question_type": "behavior",
      "questions": []
    },
    {
      "question_type": "experience",
      "questions": [
        {
          "page_text": "창의성을 발휘한 경험",
          "metadata": {
            "question_id": "HR-HRGeneralist-015",
            "question_type": "experience",
            "competency_tags": [
              "creativity",
              "problem_solving"
            ],
            "difficulty": 3,
            "job_family": "HR",
            "position": "HR 제너럴리스트 (인사 총무 담당자)",
            "level": "신입",
            "source": "잡코리아-코오롱그룹",
            "feature": "question",
            "question_text": [
              "가장 창의성을 발휘해본 경험은 무엇인가?",
              "기존 방식이 아닌 새로운 아이디어로 문제를 해결해 본 경험을 설명해 주세요.",
              "남들과 다른 방식으로 접근해 성과를 냈던 사례가 있다면 말해 주세요."
            ]
          }
        }
      ]
    },
    {
      "question_type": "tech",
      "questions": [
        {
          "page_text": "직무 관련 최신 이슈에 대한 관심",
          "metadata": {
            "question_id": "HR-HRGeneralist-018",
            "question_type": "tech",
            "competency_tags": [
              "job_knowledge",
              "communication"
            ],
            "difficulty": 3,
            "job_family": "HR",
            "position": "HR 제너럴리스트 (인사 총무 담당자)",
            "level": "신입",
            "source": "잡코리아-LG디스플레이",
            "feature": "question",
            "question_text": [
              "최근 관심 있는 직무 관련 이슈는 무엇인가? 자세히 설명하시오.",
              "최근 인사/조직 분야에서 주목하고 있는 이슈가 있다면 무엇인가요?",
              "관심 있게 보고 있는 HR 관련 사회/산업 이슈와, 그에 대한 본인의 의견을 말해 주세요."
            ]
          }
        }
      ]
    }
  ]
}

####### /search-documents (RAG 컨텍스트 확인)

{
  "job_family": "HR",
  "question": "가장 몰입해서 했던 경험은 무엇인가?",
  "answer": "대학교 때 동아리 프로젝트를 하면서 하루에 8시간씩 몰입해서 UX 리서치를 했던 경험이 있습니다...",
  "top_k": 3
}

{
  "top_question_docs": [
    {
      "page_content": "가장 몰입했던 경험",
      "metadata": {
        "question_id": "HR-HRGeneralist-014",
        "question_type": "experience",
        "competency_tags": [
          "self_awareness",
          "tenacity"
        ],
        "difficulty": 2,
        "job_family": "HR",
        "position": "HR 제너럴리스트 (인사 총무 담당자)",
        "level": "신입",
        "source": "잡코리아-코오롱그룹",
        "feature": "question",
        "question_text": [
          "가장 몰입해서 했던 경험은 무엇인가?",
          "시간 가는 줄 모르고 몰입했던 경험을 하나 말씀해 주세요.",
          "가장 열정을 쏟았던 활동과 그때의 역할, 느낀 점을 설명해 주세요."
        ]
      }
    },
    {
      "page_content": "도전 경험과 성취 경험",
      "metadata": {
        "question_id": "HR-HRManager-011",
        "question_type": "tenacity",
        "competency_tags": [
          "resilience",
          "problem_solving"
        ],
        "difficulty": 3,
        "job_family": "HR",
        "position": "HR 매니저 (인사 관리자)",
        "level": "신입",
        "source": "잡코리아-롯데그룹",
        "feature": "question",
        "question_text": [
          "본인의 도전경험을 말해보세요.",
          "다른사람에게 칭찬받았던 경험은 무엇인가요?",
          "남들이 다 어려워하는것을 본인이 쉽게 해설해서 분석했던 경험은?",
          "어려운 과제를 스스로 도전하여 성과를 냈던 사례가 있다면 알려 주세요."
        ]
      }
    },
    {
      "page_content": "당사 행사 참여 경험",
      "metadata": {
        "question_id": "HR-HRGeneralist-019",
        "question_type": "experience",
        "competency_tags": [
          "communication",
          "self_awareness"
        ],
        "difficulty": 1,
        "job_family": "HR",
        "position": "HR 제너럴리스트 (인사 총무 담당자)",
        "level": "신입",
        "source": "잡코리아-LG디스플레이",
        "feature": "question",
        "question_text": [
          "당사가 주최한 행사에 참여한 적 있는가?",
          "당사의 채용 박람회, 직무 설명회, 공모전 등 행사에 참여한 경험이 있다면 소개해 주세요.",
          "행사에 참여했다면 가장 인상 깊었던 점과, 그 경험이 지원 동기에 어떤 영향을 주었는지 말해 주세요."
        ]
      }
    }
  ],
  "top_answer_docs": [
    {
      "page_content": "제가 가장 몰입해서 했던 경험은 학부 시절 참여했던 프로젝트형 수업입니다. 당시 한 학기 동안 팀을 이뤄 실제 기업의 조직문제 사례를 분석하고 해결안을 제시하는 과제가 주어졌습니다. 처음에는 사례와 자료가 방대해서 막막했지만, 어느 순간부터 문제의 구조가 보이기 시작하면서 자연스럽게 관련 논문과 보고서를 찾아보는 시간이 늘어났습니다. 수업이 끝난 뒤에도 팀원들과 남아서 토론을 이어가다 보니, 시간 가는 줄 모르고 밤늦게까지 교내 스터디룸에 남아 있던 날도 많았습니다. 그 과정에서 분석 결과를 인사제도와 교육, 조직문화 개선안으로 연결해 발표했고, 교수님께 좋은 피드백을 받았습니다. 이 경험을 통해 저는 ‘사람과 조직’을 주제로 한 문제를 깊이 파고들 때 가장 몰입한다는 것을 깨달았고, 자연스럽게 HR 직무에 대한 관심으로 이어지게 되었습니다.",
      "metadata": {
        "answer_id": "HR-HRGeneralist-014-ans",
        "question_text": "가장 몰입해서 했던 경험은 무엇인가?",
        "question_id": "HR-HRGeneralist-014",
        "question_type": "experience",
        "competency_tags": [
          "self_awareness",
          "tenacity"
        ],
        "structure_name": "STAR",
        "job_family": "HR",
        "position": "HR 제너럴리스트 (인사 총무 담당자)",
        "level": "신입",
        "feature": "answer"
      }
    },
    {
      "page_content": "제가 가장 기억에 남는 도전 경험은 준비 기간이 짧았던 팀 프로젝트에서, 낯선 도구를 활용해 결과를 내야 했던 상황입니다. 처음에는 팀 모두가 막막해했지만, 저는 역할을 나누고 필요한 기술을 빠르게 학습하는 방향으로 계획을 세웠습니다. 밤늦게까지 문서를 찾아보고, 간단한 프로토타입을 만들어 팀원들과 공유하며 수정해 나갔습니다. 그 결과, 기대했던 것보다 완성도 높은 결과물을 제출할 수 있었고, 짧은 시간 안에도 방향성을 잘 잡으면 충분히 해낼 수 있다는 자신감을 얻게 되었습니다.",
      "metadata": {
        "answer_id": "HR-HRManager-011-ans",
        "question_text": "본인의 도전경험을 말해보세요.",
        "question_id": "HR-HRManager-011",
        "question_type": "tenacity",
        "competency_tags": [
          "resilience",
          "problem_solving"
        ],
        "structure_name": "SOARA",
        "job_family": "HR",
        "position": "HR 매니저 (인사 관리자)",
        "level": "신입",
        "feature": "answer"
      }
    },
    {
      "page_content": "가장 창의성을 발휘했던 경험은, 동아리에서 진행했던 교내 행사 홍보 방식 개선 프로젝트였습니다. 매년 비슷한 포스터와 부스 홍보만 이어지다 보니 참여율이 떨어지는 것이 고민이었습니다. 저는 기존 방식에서 벗어나, 학생들이 자주 사용하는 SNS와 메신저를 활용한 참여형 이벤트를 제안했습니다. 단순 홍보 글이 아니라, 밈 형식의 짧은 콘텐츠와 투표 기능을 활용해 행사 주제와 관련된 질문을 올리고, 참여 학생들에게는 소정의 굿즈를 제공하는 구조였습니다. 그 결과 이전보다 사전 신청 인원이 크게 늘었고, 행사 당일에도 참여율이 눈에 띄게 높아졌습니다. 이 경험을 통해 작은 아이디어라도 기존 틀을 한 번 더 의심하고, ‘사용자 입장에서 더 재밌고 편한 방식이 무엇일까’를 고민하는 것이 창의성의 시작이라는 것을 배웠습니다.",
      "metadata": {
        "answer_id": "HR-HRGeneralist-015-ans",
        "question_text": "가장 창의성을 발휘해본 경험은 무엇인가?",
        "question_id": "HR-HRGeneralist-015",
        "question_type": "experience",
        "competency_tags": [
          "creativity",
          "problem_solving"
        ],
        "structure_name": "STAR",
        "job_family": "HR",
        "position": "HR 제너럴리스트 (인사 총무 담당자)",
        "level": "신입",
        "feature": "answer"
      }
    }
  ],
  "competency_docs": [
    {
      "page_content": "문제 해결력은 주어진 제약 조건 하에서 문제를 정의하고 해결책을 찾는 능력입니다.\n좋은 예: 문제를 구조적으로 분석하고 해결 과정을 단계적으로 설명한다.\n나쁜 예: 문제의 원인을 명확히 제시하지 못하거나 해결책이 모호하다.",
      "metadata": {
        "competency_id": "problem_solving",
        "competency_name": "문제 해결력",
        "importance": 5
      }
    },
    {
      "page_content": "회복탄력성(resilience)은 실패·갈등·압박 속에서도 다시 일어나 지속적으로 수행하는 능력입니다.\n좋은 예: 위기 상황을 어떻게 극복했는지 감정 조절 과정까지 설명한다.\n나쁜 예: 힘들었다는 감정만 얘기하고 극복 과정이 없다.",
      "metadata": {
        "competency_id": "resilience",
        "competency_name": "회복탄력성",
        "importance": 4
      }
    },
    {
      "page_content": "창의력은 기존 방식에만 의존하지 않고 새로운 해결책이나 접근을 제시하는 능력입니다.\n좋은 예: 제약 상황에서도 새로운 아이디어로 문제를 해결한 사례를 설명한다.\n나쁜 예: 단순히 '발상이 독특하다'라고만 하고 실제 구현 경험이 없다.",
      "metadata": {
        "competency_id": "creativity",
        "competency_name": "창의력",
        "importance": 3
      }
    },
    {
      "page_content": "자기 이해는 자신의 강점·약점·가치관·선호 환경을 객관적으로 아는 능력입니다.\n좋은 예: 피드백과 경험을 통해 정리한 자신만의 핵심 강점·약점을 말한다.\n나쁜 예: 강점은 '성실함', 약점은 '완벽주의' 정도로만 말한다.",
      "metadata": {
        "competency_id": "self_awareness",
        "competency_name": "자기 이해",
        "importance": 5
      }
    },
    {
      "page_content": "끈기는 어려움이 있어도 목표를 포기하지 않고 계속해서 시도하는 태도입니다.\n좋은 예: 장기간 준비가 필요한 자격증·프로젝트를 끝까지 해낸 경험을 말한다.\n나쁜 예: 조금 힘들면 목표를 바꿔버리는 패턴이 반복된다.",
      "metadata": {
        "competency_id": "tenacity",
        "competency_name": "끈기",
        "importance": 4
      }
    }
  ],
  "answer_pattern_docs": [
    {
      "page_content": "경험형 질문에는 STAR 구조를 활용하세요:\n- Situation: 상황 설명\n- Task: 과제 설명\n- Action: 행동\n- Result: 결과",
      "metadata": {
        "pattern_id": "pattern_star_exp",
        "question_type": "experience",
        "structure_name": "STAR",
        "feature": "answer_patterns"
      }
    },
    {
      "page_content": "끈기·문제해결 질문에는 SOARA 구조를 활용하세요:\n- Situation: 문제 상황\n- Objective: 목표 설정\n- Action: 시도한 행동\n- Result: 결과\n- Aftermath: 배운 점 및 다음 적용",
      "metadata": {
        "pattern_id": "pattern_soara_tenacity",
        "question_type": "tenacity",
        "structure_name": "SOARA",
        "feature": "answer_patterns"
      }
    }
  ]
}