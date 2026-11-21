import pytest
from core import connect,ingest,retrieve,validate,approve

def test_search():
    db=connect(':memory:')
    assert ingest(db,'notes.txt',b'Calibration report due Friday.')==1
    assert ingest(db,'notes.txt',b'Calibration report due Friday.')==0
    assert retrieve(db,'calibration')[0]['name']=='notes.txt'

def test_validation():
    with pytest.raises(ValueError): validate({'citations':[99]},{1})

def test_approval():
    db=connect(':memory:')
    ingest(db,'notes.txt',b'Write report.')
    task={'title':'Write report','deadline':'','source':1}
    approve(db,task); approve(db,task)
    assert db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]==1
