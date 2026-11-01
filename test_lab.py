import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import sqlite3
import lab
from lab import index_documents,search,task_action,experiment

class LabTests(unittest.TestCase):
    def test_retrieval_and_empty(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)/'docs'; folder.mkdir()
            (folder/'a.md').write_text('로봇 관절 속도와 회전각도',encoding='utf-8')
            (folder/'b.md').write_text('음성 인식 자막 생성',encoding='utf-8')
            index=Path(d)/'index.json'; index_documents(folder,index)
            self.assertEqual(search(index,'관절 회전')[0]['source'],'a.md')
            self.assertEqual(search(index,'zzzzzz'),[])
    def test_task_persistence_and_validation(self):
        with tempfile.TemporaryDirectory() as d:
            db=Path(d)/'tasks.db'; item=task_action(db,'add','속도 평가')[0]
            self.assertEqual(task_action(db,'set',task_id=item['id'],status='done')[0]['status'],'done')
            with self.assertRaises(ValueError): task_action(db,'set',task_id='missing',status='done')
    def test_failed_experiment_is_not_success(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fail.py'; p.write_text('raise SystemExit(3)',encoding='utf-8')
            result=experiment(p,Path(d)/'runs')
            self.assertEqual(result['returncode'],3); self.assertEqual(result['metrics'],{})
    def test_task_db_connection_is_closed(self):
        # Windows에서 DB 파일 잠금이 남지 않도록 연결을 닫는지 확인한다.
        opened=[]
        real=sqlite3.connect
        def tracking(*a,**kw):
            conn=real(*a,**kw); opened.append(conn); return conn
        with tempfile.TemporaryDirectory() as d, mock.patch.object(lab.sqlite3,'connect',side_effect=tracking):
            task_action(Path(d)/'tasks.db','add','닫힘 확인')
            with self.assertRaises(sqlite3.ProgrammingError): opened[0].execute('SELECT 1')
    def test_missing_index_gives_guidance(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError) as cm: search(Path(d)/'index.json','관절')
            self.assertIn('index',str(cm.exception))
    def test_experiment_korean_output_and_metrics(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'ok.py'
            p.write_text("import json\nprint('한국어 출력 ✓')\nprint(json.dumps({'mae':0.5,'flag':True}))",encoding='utf-8')
            result=experiment(p,Path(d)/'runs')
            self.assertEqual(result['returncode'],0); self.assertEqual(result['metrics'],{'mae':0.5})
            out=next((Path(d)/'runs').glob('*/stdout.txt')).read_text(encoding='utf-8')
            self.assertIn('한국어 출력 ✓',out)

if __name__=='__main__': unittest.main()
