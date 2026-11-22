# 에이전트 연구실 (hyoki-agent-lab)

> **관련 저장소 구분** — 이 저장소는 **경량 CLI 패키지판**입니다: BM25 검색, Ollama RAG, 칸반 작업, 수치를 직접 입력하는 실험 기록을 `python -m agentlab` 하나로 씁니다.
> 실험 스크립트를 실제로 실행·기록하고 임베딩 RAG를 쓰는 **실행형 정식판**은 [research-workbench](https://github.com/MetaSonGi/research-workbench)입니다.


내 문서를 검색하고(BM25), 검색 결과로 Ollama에게 답을 받는 **RAG**, 그리고 **작업 관리·실험 기록·결과 비교**를 하나로 묶은 명령줄 도구예요. 외부 패키지 없이 Python 표준 라이브러리만 써요.

## 사용법

```bash
# 문서 검색 (.md, .txt)
python -m agentlab search docs "정지 명령 처리"

# RAG 질문 (Ollama 실행 필요). --dry-run이면 프롬프트만 출력
python -m agentlab ask docs "정지 명령은 어떻게 처리해?" --dry-run
python -m agentlab ask docs "정지 명령은 어떻게 처리해?" --model llama3.2

# 작업 관리: todo → doing → review → done
python -m agentlab task add 음성 인식 연결 --done-when "명령 5개 인식 후 로그 기록"
python -m agentlab task move 1 doing
python -m agentlab task list

# 실험 기록과 비교 (OpenResearch식: 가설 → 실험 → 결과)
python -m agentlab run bm25-k3 --hypothesis "k=3이면 충분" --params '{"k":3}' --metrics '{"acc":0.7}'
python -m agentlab compare acc
```

데이터는 `lab.json`에 저장돼요 (`--store`로 경로 변경).

## 예시 문서

`docs/`에 로봇 프로젝트 예시 문서가 있어요. 내 문서로 바꿔 쓰면 돼요.

## 테스트

```bash
python -m pytest
```
