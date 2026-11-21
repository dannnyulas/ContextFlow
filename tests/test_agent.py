import pytest
from core import connect, ingest
from agent import run_agent

def scripted(*actions):
    iterator=iter(actions)
    return lambda messages: next(iterator)

def test_agent_selects_tools_and_proposes_without_writing():
    db=connect(':memory:'); ingest(db,'notes.txt',b'Maya will submit the report by 2026-12-01.')
    model=scripted({'tool':'search','args':{'query':'report'}},{'tool':'extract_tasks'},{'tool':'finish','answer':'Report due','citations':[1],'tasks':[{'title':'Maya will submit the report','deadline':'2026-12-01','source':1}]})
    hits,result,trace,done=run_agent(db,'Find tasks',model=model)
    assert done and len(trace)==2 and len(result['tasks'])==1
    assert db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]==0

def test_unknown_tool_rejected():
    with pytest.raises(ValueError): run_agent(connect(':memory:'),'test',model=scripted({'tool':'shell'}))

def test_step_limit():
    result=run_agent(connect(':memory:'),'test',model=lambda _: {'tool':'list_tasks'},max_steps=2)
    assert not result[3] and len(result[2])==2

def test_invalid_citation():
    with pytest.raises(ValueError): run_agent(connect(':memory:'),'test',model=scripted({'tool':'finish','citations':[99]}))
