from core import connect, ingest
from workflows import run_workflow, export_tasks, approve
from evaluate import evaluate


def test_approval_boundary():
    db = connect(':memory:')
    ingest(db,'notes.txt',b'Maya will submit the report by 2026-12-01.')
    hits,result,_ = run_workflow(db,'report')
    assert len(result['tasks']) == 1
    assert export_tasks(db) == '[]'
    approve(db,result['tasks'][0])
    assert 'Maya will submit the report' in export_tasks(db)


def test_smoke_benchmark():
    result = evaluate()
    assert result['recall_at_3'] == 1
    assert result['local_task_recall'] == 1
