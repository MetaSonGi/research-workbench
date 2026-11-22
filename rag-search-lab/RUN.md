# 실행 방법

Python 3.10 이상에서 추가 패키지 없이 실행합니다.

```bash
python app.py
```

브라우저: http://localhost:8766

개인 로컬 MVP입니다. 서버는 127.0.0.1에만 열리며 인터넷에 배포하지 마세요.
생성 데이터는 같은 폴더의 SQLite 파일에 저장됩니다. 테스트: `python -m unittest -v test_app.py`.

## 선택: 실제 LLM 생성
Ollama를 설치하고 원하는 생성 모델을 미리 내려받은 뒤 서버를 실행하세요.

PowerShell: `$env:OLLAMA_MODEL="설치한-모델명"; python app.py`

macOS/Linux: `OLLAMA_MODEL=설치한-모델명 python app.py`

모델을 지정하지 않으면 검색된 원문만 보여주는 retrieval-only 모드입니다.
이 버전의 임베딩은 외부 모델 없는 문자 n-gram 해시 벡터이며, 신경망 의미 임베딩이 아닙니다.
SQLite에 벡터를 저장하고 작은 문서 집합을 전수 코사인 검색합니다. 대규모 ANN 엔진은 후속 작업입니다.
