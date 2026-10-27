# 효기 에이전트 연구실

문서 근거 검색, 선택적 Ollama RAG, 역할별 수동 작업 큐와 로컬 Python 실험 결과를 관리하는 워크벤치입니다. **자율 멀티 에이전트·브라우저 조작·실제 로봇 제어는 구현하지 않았습니다.**

## 바로 실행 — Python 3.11+, 추가 패키지 없음

```bash
python lab.py index .
python lab.py search "관절 회전 시간"
python lab.py task add --title "관절 속도별 예측 오차 평가" --role researcher
python lab.py task list
python lab.py run experiment.py
python lab.py compare
```

기본 검색은 **키워드+한국어 문자 bigram 기준선**입니다. 임베딩·LLM을 실행한 것처럼 표시하지 않습니다. 예제 실험 데이터는 합성 데이터이며 실제 로봇 측정치가 아닙니다.

## 임베딩·RAG — Ollama 선택 연결

본인 PC에서 Ollama와 원하는 임베딩/생성 로컬 모델을 미리 설치하세요.

```bash
python lab.py index . --embed-model YOUR_EMBED_MODEL
python lab.py ask "관절 회전 시간은 어떻게 구하나요?" --model YOUR_CHAT_MODEL
```

모델명을 `ollama list`에 있는 실제 모델로 바꾸세요. `/api/embed`, `/api/generate`를 `127.0.0.1:11434`에 호출합니다. 인덱스는 JSON 벡터 목록을 완전 탐색하는 소규모 구현이며 외부 Vector DB 서버가 아닙니다. 모델 변경 시 다시 index 하세요. PDF·이미지 OCR은 지원하지 않습니다.

문서의 source·offset·id와 유사도 점수를 반환합니다. 근거 없음은 별도 반환하고 문서 속 지시를 따르지 않도록 시스템 지시를 분리했지만, LLM의 사실성과 인용은 사람이 검토해야 합니다.

## 작업 상태 변경

```bash
python lab.py task set --id RETURNED_TASK_ID --status doing
```

지원 상태: todo, doing, review, done. role은 사람이 정하는 작업 분류입니다. 작업을 추가해도 외부 에이전트가 자동 실행되지는 않습니다.

## 실험 계약과 기록

`run`은 사용자가 지정한 **신뢰하는 Python 파일**을 현재 Python으로 실제 실행합니다. 샌드박스가 아니므로 다른 사람이 준 파일이나 AI 생성 코드를 검토 없이 실행하지 마세요. 웹 API로 임의 명령을 실행하는 기능은 없습니다.

- 실험의 마지막 stdout 줄이 JSON 객체이면 숫자 항목을 metrics로 저장
- 스크립트 SHA-256, 종료 코드, 실행 시간, stdout/stderr 보관
- 실패·타임아웃을 성공으로 처리하지 않음
- 기본 제한 60초, `--timeout`으로 변경 가능
- `data/runs/`를 지우면 실험 기록이 사라지므로 별도 백업

데이터는 `data/`에 저장되며 Git 제외입니다. 별도 위치는 `python lab.py --data PATH ...`. 연결 모델이 외부 서비스를 쓰면 로컬 UI·기록과 별개로 데이터가 전송될 수 있습니다.

## 검증

```bash
python -m unittest -v
```

키워드 근거 순위·근거 없음·작업 영속성·실험 실패 기록 검증. 실제 Ollama 추론과 실장비 동작은 검증하지 않았습니다.

참조: [Ollama embed API](https://docs.ollama.com/api/embed), [generate API](https://docs.ollama.com/api/generate).
