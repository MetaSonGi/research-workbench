import json
from pathlib import Path
import tempfile
import unittest
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

if __name__=='__main__': unittest.main()
