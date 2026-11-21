import json
from pathlib import Path
from core import connect, ingest, retrieve
from workflows import propose_local


def evaluate():
    db = connect(':memory:')
    for path in sorted((Path(__file__).parent / 'demo').glob('*.txt')):
        ingest(db, path.name, path.read_bytes())
    cases = [('calibration report','meeting.txt'),('enclosure diameter','requirements.txt'),('procurement budget','schedule.txt'),('safety checklist','meeting.txt'),('5 V supply','requirements.txt'),('design review slides','schedule.txt')]
    ranks = []
    for query, expected in cases:
        hits = retrieve(db,query,k=3)
        ranks.append(next((i+1 for i,r in enumerate(hits) if r['name']==expected),0))
    proposals = propose_local([dict(r) for r in db.execute('SELECT * FROM chunks')])['tasks']
    expected = {('Maya will submit the calibration report','2026-11-30'),('Alex will review the safety checklist','2026-12-02'),('Maya will prepare the design review slides','2026-12-03')}
    actual = {(t['title'],t['deadline']) for t in proposals}
    tp = len(actual & expected)
    return {'dataset':'small synthetic smoke-test fixture','queries':len(cases),'recall_at_1':sum(r==1 for r in ranks)/len(ranks),'recall_at_3':sum(r>0 for r in ranks)/len(ranks),'mrr':sum(1/r if r else 0 for r in ranks)/len(ranks),'local_task_precision':tp/len(actual) if actual else 0,'local_task_recall':tp/len(expected),'expected_tasks':len(expected)}

if __name__ == '__main__':
    print(json.dumps(evaluate(),indent=2))
