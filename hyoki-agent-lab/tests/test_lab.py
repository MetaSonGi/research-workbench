import pytest

from agentlab import lab, rag
from agentlab.search import Chunk, Index, chunk_text


def test_chunk_overlap():
    parts = chunk_text("a" * 1000, size=400, overlap=100)
    assert len(parts) == 3 and all(len(p) <= 400 for p in parts)
    with pytest.raises(ValueError):
        chunk_text("abc", 10, 10)


def test_search_ranks_relevant_chunk_first():
    idx = Index([Chunk("a.md", 0, "Unity 관절 제어와 ROS 2 통신 설정"),
                 Chunk("b.md", 0, "Whisper 음성 인식으로 명령어를 받아요"),
                 Chunk("c.md", 0, "점심 메뉴 추천")])
    hits = idx.search("음성 인식 명령")
    assert hits[0][1].source == "b.md"
    assert all(h[1].source != "c.md" for h in hits)


def test_korean_particles_still_match():
    idx = Index([Chunk("a.md", 0, "로봇팔은 정지명령을 받으면 멈춥니다")])
    assert idx.search("정지명령")


def test_from_folder(tmp_path):
    (tmp_path / "doc.md").write_text("RAG는 검색 증강 생성이에요", encoding="utf-8")
    (tmp_path / "skip.py").write_text("print('x')", encoding="utf-8")
    idx = Index.from_folder(tmp_path)
    assert len(idx.chunks) == 1


def test_prompt_contains_sources():
    prompt = rag.build_prompt("RAG가 뭐야?", [(1.0, Chunk("doc.md", 0, "RAG 설명"))])
    assert "[1] (doc.md#0)" in prompt and "RAG가 뭐야?" in prompt


def test_tasks_and_runs(tmp_path):
    store = lab.Store(tmp_path / "lab.json")
    t = store.add_task("음성 인식 연결", "명령 5개 인식 후 로그 기록")
    store.move(t["id"], "doing")
    with pytest.raises(ValueError):
        store.move(t["id"], "nope")
    store.log_run("bm25-k3", "k=3이 충분", {"k": 3}, {"acc": 0.7})
    store.log_run("bm25-k5", "k=5가 낫다", {"k": 5}, {"acc": 0.8})
    reloaded = lab.Store(tmp_path / "lab.json")
    assert reloaded.data["tasks"][0]["status"] == "doing"
    assert reloaded.compare("acc")[0]["name"] == "bm25-k5"
    assert "bm25-k5" in lab.table(reloaded.compare("acc"), "acc")
