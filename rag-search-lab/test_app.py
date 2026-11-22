import unittest, tempfile
from pathlib import Path
import app
class RetrievalTest(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.old=app.ROOT;app.ROOT=Path(self.temp.name)
 def tearDown(self):app.ROOT=self.old;self.temp.cleanup()
 def test_retrieval_and_replace(self):
  app.ingest('robot','로봇 작업 좌표는 도구 끝단의 위치와 방향입니다.')
  app.ingest('garden','토마토는 햇빛을 받고 자랍니다.')
  self.assertEqual(app.search('로봇 작업 좌표',1)[0]['source'],'robot')
  app.ingest('robot','새로 수정한 로봇 매뉴얼')
  with app.db() as c:self.assertEqual(c.execute("SELECT count(*) FROM chunks WHERE source='robot'").fetchone()[0],1)
 def test_no_evidence_and_validation(self):
  self.assertEqual(app.post('/api/ask',{'question':'로봇','k':3})['mode'],'no-evidence')
  for k in (0,11,True):
   with self.assertRaises(ValueError):app.search('a',k)
 def test_embed_and_chunk(self):
  v=app.embed('로봇 작업');self.assertAlmostEqual(sum(x*x for x in v),1)
  text='가'*1100;parts=app.chunks(text);self.assertEqual(len(parts),3);self.assertEqual(parts[0][-80:],parts[1][:80])
 def test_retrieval_mode_is_explicit(self):
  import os
  previous=os.environ.pop('OLLAMA_MODEL',None)
  try:
   app.ingest('x','로봇 작업 좌표는 도구 끝단 위치입니다.');r=app.post('/api/ask',{'question':'로봇 작업 좌표','k':1});self.assertEqual(r['mode'],'retrieval-only');self.assertTrue(r['hits'])
  finally:
   if previous is not None:os.environ['OLLAMA_MODEL']=previous
if __name__=='__main__':unittest.main()
