"""RAG: 검색 결과로 프롬프트를 만들고 Ollama로 답변."""
from __future__ import annotations

import json
import urllib.request

from .search import Chunk

PROMPT = """아래 자료만 근거로 질문에 한국어로 답하세요.
자료에 답이 없으면 "자료에서 찾지 못했어요"라고 답하세요.
답변 끝에 근거로 쓴 자료 번호를 [1]처럼 표시하세요.

{context}

질문: {question}
답변:"""


def build_prompt(question: str, hits: list[tuple[float, Chunk]]) -> str:
    context = "\n\n".join(f"[{i}] ({c.source}#{c.index})\n{c.text}" for i, (_, c) in enumerate(hits, 1))
    return PROMPT.format(context=context or "(검색된 자료 없음)", question=question)


def ask_ollama(prompt: str, model: str = "llama3.2", host: str = "http://localhost:11434") -> str:
    req = urllib.request.Request(f"{host}/api/generate",
                                 data=json.dumps({"model": model, "prompt": prompt, "stream": False}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as res:
        return json.loads(res.read())["response"]
