import json
import re
import time
from datetime import date
from core import retrieve, generate, validate, approve


def propose_local(passages):
    # A deliberately simple baseline for explicit owner/action/date sentences.
    tasks = []
    for row in passages:
        for match in re.finditer(r'\b([A-Z][a-z]+ will [^.!?]+?) by (\d{4}-\d{2}-\d{2})\b', row['body']):
            title, deadline = match.groups()
            try:
                date.fromisoformat(deadline)
            except ValueError:
                continue
            tasks.append(dict(title=title, deadline=deadline, source=row['id']))
    return validate(dict(answer='Explicit dated actions found using the local baseline.', citations=list(dict.fromkeys(t['source'] for t in tasks)), tasks=tasks), {r['id'] for r in passages})


def run_workflow(db, question, use_ai=False, semantic=False):
    # Keep the workflow bounded: retrieve, propose, validate, then wait for approval.
    start = time.perf_counter()
    hits = retrieve(db, question, k=8, semantic=semantic)
    result = generate(hits, question, 'tasks') if use_ai else propose_local(hits)
    elapsed = time.perf_counter() - start
    with db:
        db.execute('CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, mode TEXT, elapsed REAL, hits INTEGER, proposals INTEGER)')
        db.execute('INSERT INTO runs(mode,elapsed,hits,proposals) VALUES(?,?,?,?)', ('AI' if use_ai else 'local',elapsed,len(hits),len(result['tasks'])))
    return hits, result, elapsed


def export_tasks(db):
    return json.dumps([dict(r) for r in db.execute('SELECT * FROM tasks ORDER BY deadline')], indent=2)
