"""Synthetic timing baseline; not real robot measurements."""
import json
samples=[(90,30,3.2),(60,20,3.1),(45,15,3.3)]
errors=[abs(angle/speed-observed) for angle,speed,observed in samples]
print('합성 데이터로 등속 회전 시간 기준선 평가')
print(json.dumps({'mae_seconds':sum(errors)/len(errors),'samples':len(samples)}))
