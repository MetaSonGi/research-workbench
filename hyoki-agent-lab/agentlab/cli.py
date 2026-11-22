"""사용법: python -m agentlab <search|ask|task|run|compare> ..."""
from __future__ import annotations

import argparse
import json

from . import lab, rag
from .search import Index


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="agentlab", description="에이전트 연구실")
    p.add_argument("--store", default="lab.json")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search"); s.add_argument("folder"); s.add_argument("query"); s.add_argument("-k", type=int, default=3)
    a = sub.add_parser("ask"); a.add_argument("folder"); a.add_argument("question")
    a.add_argument("--model", default="llama3.2"); a.add_argument("--dry-run", action="store_true", help="프롬프트만 출력")
    t = sub.add_parser("task"); t.add_argument("action", choices=["add", "move", "list"])
    t.add_argument("args", nargs="*"); t.add_argument("--done-when", default="")
    r = sub.add_parser("run"); r.add_argument("name"); r.add_argument("--hypothesis", default="")
    r.add_argument("--params", default="{}"); r.add_argument("--metrics", required=True)
    c = sub.add_parser("compare"); c.add_argument("metric"); c.add_argument("--lower", action="store_true")

    o = p.parse_args(argv)

    if o.cmd in ("search", "ask"):
        index = Index.from_folder(o.folder)
        hits = index.search(o.query if o.cmd == "search" else o.question, getattr(o, "k", 3))
        if o.cmd == "search":
            for score, ch in hits:
                print(f"{score:.2f}  {ch.source}#{ch.index}  {ch.text[:80]!r}")
        else:
            prompt = rag.build_prompt(o.question, hits)
            print(prompt if o.dry_run else rag.ask_ollama(prompt, o.model))
        return

    store = lab.Store(o.store)
    if o.cmd == "task":
        if o.action == "add":
            print(store.add_task(" ".join(o.args), o.done_when))
        elif o.action == "move":
            print(store.move(int(o.args[0]), o.args[1]))
        else:
            for st in lab.STATUSES:
                for task in store.data["tasks"]:
                    if task["status"] == st:
                        print(f"[{st}] #{task['id']} {task['title']}  (완료 조건: {task['done_when'] or '-'})")
    elif o.cmd == "run":
        print(store.log_run(o.name, o.hypothesis, json.loads(o.params), json.loads(o.metrics)))
    elif o.cmd == "compare":
        print(lab.table(store.compare(o.metric, not o.lower), o.metric))


if __name__ == "__main__":
    main()
