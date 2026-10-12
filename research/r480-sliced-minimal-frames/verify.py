"""Reproduce scalar/frame transformation and prospective arithmetic; physical admission separate.
Prepared for rohanarun with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import os,sys,json,hashlib,shutil,subprocess,gzip,time
if not __debug__:raise RuntimeError('Assertions must remain enabled')
P=Path(__file__).resolve().parent;O=Path(sys.argv[1]).resolve();assert not O.exists() and not O.is_relative_to(P)
manifest=json.loads((P/'MANIFEST.json').read_text());assert manifest=={f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in P.rglob('*')if f.is_file()and f!=P/'MANIFEST.json'and '__pycache__'not in f.parts}
O.mkdir(parents=True);(O/'tmp').mkdir();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(O/'tmp'));start=time.monotonic()
w=O/'bit510-review/research/e8-r480-dead-totals/data';w.mkdir(parents=True);shutil.copyfile(P/'inputs/ORIGINAL.json.gz',w/'bitE8mut-r480.json.gz')
a=O/'r480-sharp535-publication/research/r480-sharp-charge535';(a/'inputs').mkdir(parents=True);shutil.copytree(P/'engines',a/'engines')
for name in ['PR510-EXPECTED.json','PR535-EXPECTED.json']:shutil.copyfile(P/'inputs'/name,a/'inputs'/name)
shutil.copyfile(P/'inputs/PR539-EXPECTED.json',a/'EXPECTED.json')
for name in ['slice','minimum','price']:
 f=O/(name+'.py');shutil.copyfile(P/'scripts'/(name+'.py'),f)
 with (O/(name+'.log')).open('w')as log:subprocess.run([sys.executable,'-B',str(f)],cwd=O,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 print(name,'PASS',flush=True)
new=O/'bit510-sliced-minimal-frames/WORD.json.gz';assert json.loads(gzip.decompress(new.read_bytes()))==json.loads(gzip.decompress((P/'inputs/CANDIDATE.json.gz').read_bytes()))
x=json.loads((O/'bit510-sliced-minimal-price/RESULT.json').read_text());assert x==json.loads((P/'EXPECTED.json').read_text())
m=json.loads((O/'bit510-sliced-minimal-frames/RESULT.json').read_text());e=json.loads((P/'evidence/MINIMUM-FRAMES.json').read_text());assert {k:v for k,v in m.items()if k!='seconds'}=={k:v for k,v in e.items()if k!='seconds'}
r=dict(status='PASS_PACKAGED_RECONSTRUCTION_AND_PROSPECTIVE_PRICE',kappa=x['kappa_decimal'],bit=x['bit_decimal'],word_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),manifest_sha256=hashlib.sha256((P/'MANIFEST.json').read_bytes()).hexdigest(),python=sys.version,seconds=time.monotonic()-start,scope='Exact reconstruction of source slice and least frames,720 scalar columns, nesting and two rational moment engines with47 outer constraints. Prospective unchanged owner schedule and prior finite allowances; physical template and finite invoice remain pending. No completed supplier admission.')
(O/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['kappa'],flush=True)
