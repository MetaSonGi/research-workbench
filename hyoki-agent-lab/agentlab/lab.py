"""작업 관리와 실험 기록·비교 (JSON 파일 저장)."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

STATUSES = ["todo", "doing", "review", "done"]


class Store:
    def __init__(self, path: str | Path = "lab.json"):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {"tasks": [], "runs": []}

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- 작업 ----
    def add_task(self, title: str, done_when: str = "") -> dict:
        task = {"id": max((t["id"] for t in self.data["tasks"]), default=0) + 1,
                "title": title, "done_when": done_when, "status": "todo"}
        self.data["tasks"].append(task)
        self.save()
        return task

    def move(self, task_id: int, status: str) -> dict:
        if status not in STATUSES:
            raise ValueError(f"status는 {STATUSES} 중 하나")
        task = next(t for t in self.data["tasks"] if t["id"] == task_id)
        task["status"] = status
        self.save()
        return task

    # ---- 실험 ----
    def log_run(self, name: str, hypothesis: str, params: dict, metrics: dict) -> dict:
        run = {"name": name, "hypothesis": hypothesis, "params": params, "metrics": metrics,
               "at": datetime.now().isoformat(timespec="seconds")}
        self.data["runs"].append(run)
        self.save()
        return run

    def compare(self, metric: str, higher_is_better: bool = True) -> list[dict]:
        runs = [r for r in self.data["runs"] if metric in r["metrics"]]
        return sorted(runs, key=lambda r: r["metrics"][metric], reverse=higher_is_better)


def table(runs: list[dict], metric: str) -> str:
    lines = [f"| 순위 | 실험 | {metric} | 파라미터 |", "|---|---|---|---|"]
    for i, r in enumerate(runs, 1):
        lines.append(f"| {i} | {r['name']} | {r['metrics'][metric]} | {json.dumps(r['params'], ensure_ascii=False)} |")
    return "\n".join(lines)
