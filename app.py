import os
from pathlib import Path
from agent import run_agent, save_audit
from workflows import run_workflow, export_tasks
from evaluate import evaluate
import time
import streamlit as st
from core import connect,ingest,retrieve,generate,approve

st.set_page_config(page_title='ContextFlow',page_icon='📚',layout='wide')
st.title('ContextFlow')
st.caption('A personal document workspace for finding information and turning it into tasks.')
db=connect()
with st.sidebar:
    st.header('Documents')
    if st.button('Load demo workspace'):
        for path in (Path(__file__).parent / 'demo').glob('*.txt'):
            ingest(db,path.name,path.read_bytes())
        st.success('Demo documents indexed')
    files=st.file_uploader('Add documents',type=['pdf','docx','txt','md','csv'],accept_multiple_files=True)
    if st.button('Index documents'):
        for f in files or []:
            try: st.success(f'{f.name}: {ingest(db,f.name,f.getvalue())} new passages')
            except Exception as e: st.error(str(e))
    st.write([r[0] for r in db.execute('SELECT DISTINCT name FROM chunks')])
    semantic=st.checkbox('Hybrid semantic search (local Ollama)')
    st.caption('AI runs locally through Ollama. Documents and audit logs are stored locally; avoid sensitive files.')
search,tasks,metrics,agent,prompts=st.tabs(['Search and assistant','Approved tasks','Evaluation','AI agent','Prompt library'])
with search:
    query=st.text_input('What would you like to find?')
    mode=st.radio('Mode',['Search only','Ask AI','Extract tasks','Extract tasks locally'],horizontal=True)
    if st.button('Run',disabled=not query.strip()):
        st.session_state.pop('result',None)
        try:
            start=time.perf_counter()
            if mode in ('Extract tasks','Extract tasks locally'):
                hits,result,_=run_workflow(db,query,use_ai=mode=='Extract tasks',semantic=semantic)
            else:
                hits=retrieve(db,query,semantic=semantic)
                result=generate(hits,query) if mode=='Ask AI' else None
            st.session_state.result=(hits,result,time.perf_counter()-start)
        except Exception as e: st.error(str(e))
    if 'result' in st.session_state:
        hits,result,elapsed=st.session_state.result
        st.caption(f'Processed in {elapsed:.2f} seconds')
        if result:
            st.write(result['answer'])
            st.caption('Referenced passage IDs: '+str(result['citations']))
            for i,t in enumerate(result['tasks']):
                st.write(f"{t['title']} | {t['deadline'] or 'No deadline'} | Source {t['source']}")
                if st.button('Approve task',key=f'approve{i}'):
                    approve(db,t); st.success('Saved')
        for r in hits:
            with st.expander(f"[{r['id']}] {r['name']} — page {r['page']}"):
                st.write(r['body'])
with tasks:
    st.download_button('Export tasks as JSON',export_tasks(db),file_name='tasks.json')
    for t in db.execute('SELECT * FROM tasks ORDER BY deadline'):
        c,b=st.columns([4,1]); c.write(f"{t['title']} — {t['deadline'] or 'No deadline'} ({t['status']})")
        if b.button('Toggle status',key=f"task{t['id']}"):
            with db: db.execute('UPDATE tasks SET status=? WHERE id=?',('done' if t['status']=='open' else 'open',t['id']))
            st.rerun()
with metrics:
    st.caption('Synthetic smoke test only; not a production accuracy estimate.')
    if st.button('Run local benchmark'):
        st.json(evaluate())
    db.execute('CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, mode TEXT, elapsed REAL, hits INTEGER, proposals INTEGER)')
    st.dataframe([dict(r) for r in db.execute('SELECT * FROM runs ORDER BY id DESC')])
with agent:
    st.caption('The agent selects read-only tools, observes results and decides what to do next. Task writes require your approval.')
    objective=st.text_area('Agent objective', key='objective')
    if st.button('Run agent',disabled=not objective.strip()):
        st.session_state.pop('agent_result',None)
        try:
            with st.spinner('Running local agent...'):
                hits,result,trace,completed=run_agent(db,objective,semantic=semantic)
                save_audit(db,objective,trace,completed)
                st.session_state.agent_result=(hits,result,trace,completed)
        except Exception as e: st.error(f'Agent stopped: {e}')
    if 'agent_result' in st.session_state:
        hits,result,trace,completed=st.session_state.agent_result
        st.caption('Model returned final answer' if completed else 'Stopped at step limit')
        st.write(result['answer'])
        st.write('Citations:',result['citations'])
        for step in trace:
            with st.expander(f"Step {step['step']}: {step['tool']}"): st.json(step)
        for r in hits:
            with st.expander(f"Source {r['id']}: {r['name']} — page {r['page']}"): st.write(r['body'])
        for i,t in enumerate(result['tasks']):
            st.write(t)
            if st.button('Approve proposed task',key=f'agent_approve_{i}'):
                approve(db,t); st.success('Saved')
    db.execute('CREATE TABLE IF NOT EXISTS agent_runs(id INTEGER PRIMARY KEY, created TEXT DEFAULT CURRENT_TIMESTAMP, objective TEXT, trace TEXT, completed INTEGER)')
    with st.expander('Past agent runs'):
        for r in db.execute('SELECT * FROM agent_runs ORDER BY id DESC LIMIT 10'):
            st.write(r['created'],r['objective']); st.json(r['trace'])
with prompts:
    db.execute('CREATE TABLE IF NOT EXISTS prompts(id INTEGER PRIMARY KEY, name TEXT, body TEXT)')
    name=st.text_input('Prompt name'); body=st.text_area('Prompt text')
    if st.button('Save prompt',disabled=not(name.strip() and body.strip())):
        with db: db.execute('INSERT INTO prompts(name,body) VALUES(?,?)',(name,body))
    for p in db.execute('SELECT * FROM prompts ORDER BY id DESC'):
        st.write(p['name']); st.code(p['body'],language=None)
db.close()
