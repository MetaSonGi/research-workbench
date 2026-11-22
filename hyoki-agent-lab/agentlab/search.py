"""문서 검색: 의존성 없는 BM25 + 청크 분할."""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

TOKEN = re.compile(r"[0-9A-Za-z]+|[가-힣]+")


def tokenize(text: str) -> list[str]:
    tokens = []
    for t in TOKEN.findall(text.lower()):
        tokens.append(t)
        if re.fullmatch(r"[가-힣]{3,}", t):  # 한국어 조사 대응: 2글자 n-gram 추가
            tokens += [t[i:i + 2] for i in range(len(t) - 1)]
    return tokens


@dataclass
class Chunk:
    source: str
    index: int
    text: str


def chunk_text(text: str, size: int = 500, overlap: int = 100) -> list[str]:
    if overlap >= size:
        raise ValueError("overlap은 size보다 작아야 해요.")
    text = text.strip()
    if not text:
        return []
    out, start = [], 0
    while start < len(text):
        out.append(text[start:start + size])
        if start + size >= len(text):
            break
        start += size - overlap
    return out


class Index:
    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks, self.k1, self.b = chunks, k1, b
        self.tfs = [Counter(tokenize(c.text)) for c in chunks]
        self.lens = [sum(tf.values()) for tf in self.tfs]
        self.avg = (sum(self.lens) / len(self.lens)) if self.lens else 0
        df = Counter(t for tf in self.tfs for t in tf)
        n = len(chunks)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    @classmethod
    def from_folder(cls, folder: str | Path, size: int = 500, overlap: int = 100) -> "Index":
        chunks = []
        for path in sorted(Path(folder).rglob("*")):
            if path.suffix.lower() in {".md", ".txt"}:
                for i, part in enumerate(chunk_text(path.read_text(encoding="utf-8"), size, overlap)):
                    chunks.append(Chunk(str(path), i, part))
        return cls(chunks)

    def search(self, query: str, k: int = 3) -> list[tuple[float, Chunk]]:
        q = tokenize(query)
        scored = []
        for chunk, tf, length in zip(self.chunks, self.tfs, self.lens):
            score = 0.0
            for t in q:
                if t in tf:
                    f = tf[t]
                    score += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / (self.avg or 1)))
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda x: -x[0])
        return scored[:k]
