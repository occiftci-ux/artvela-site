"""Lebriz görsel denetimi: kaydedilmiş BÜTÜN sayfalardaki (dergi, sergi, sanatçı, müzayede; klasör ve zip paketleri)
imageHandler bağlantılarını toplar, indirilmiş olanlarla karşılaştırır, eksikleri gorseller/bekleyen.tsv'ye yazar
(anahtar \t sorgu). gorsel_cek.py bu kuyruğu önce işler. Kullanım: gorsel_denetim.py <koruma>
Sebep (11 Kasım): gorsel_cek.py tur süresi dolunca bellekteki kuyruğu atıyor, sayfaları ise taranmış sayıyordu."""
import os,re,sys,gzip,glob,html,zipfile,collections,urllib.parse
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import paket
K=sys.argv[1]; G=os.path.join(K,'gorseller')
IMG=re.compile(r'imageHandler\.ashx\?([^"\'\s>]+)')
def key(q): return (q.get('iPath','').strip('/')+'/'+q.get('iName','')).strip('/')
done=set()
for l in open(os.path.join(G,'manifest.tsv'),encoding='utf-8'):
  f=l.rstrip('\n').split('\t')
  if len(f)>=2: done.add(f[1])
D=paket.dizin(K)
done|={r[10:-4] for r in D if r.startswith('gorseller/') and r.endswith('.jpg')}
bad=collections.Counter()
ep=os.path.join(G,'hatalar.tsv')
if os.path.exists(ep):
  for l in open(ep,encoding='utf-8'):
    f=l.split('\t')
    if len(f)>1 and 'Input/output' not in l: bad[f[1]]+=1
eks={}; tur=collections.Counter(); hepsi=set(); sayfa=0
def isle(t,rel):
  global sayfa; sayfa+=1
  tip=rel.split('/')[0]
  for m in IMG.finditer(t):
    p=dict(urllib.parse.parse_qsl(html.unescape(m.group(1))))
    if not p.get('iName'): continue
    k=key(p); hepsi.add(k)
    if k not in done and k not in eks: eks[k]=urllib.parse.urlencode(p); tur[(tip,k.split('/')[0])]+=1
# klasördeki sayfalar
gor=set()
for R in paket.koklar(K):
  for pat in ['sayfalar/**/*.html.gz','muzayede/sayfalar/**/*.html.gz']:
    for f in glob.glob(os.path.join(R,pat),recursive=True):
      rel=os.path.relpath(f,R)
      try: isle(gzip.decompress(open(f,'rb').read()).decode('utf-8','ignore'),rel); gor.add(paket.kanonik(rel))
      except Exception as e: print('HATA',f,e,flush=True)
# paketlerdeki sayfalar, zip zip
zips=collections.defaultdict(list)
for r,z in D.items():
  if (r.startswith('sayfalar/') or r.startswith('muzayede/')) and r.endswith('.html.gz') and r not in gor: zips[z].append(r)
for i,(z,rs) in enumerate(sorted(zips.items())):
  try:
    zp=paket.zip_yolu(K,z)
    with zipfile.ZipFile(zp) as zf:
      for r in rs:
        try: isle(gzip.decompress(zf.read(r)).decode('utf-8','ignore'),r)
        except Exception as e: print('HATA',r,e,flush=True)
    paket._Z.pop(z,None)
    if zp.startswith(paket.ONBELLEK): os.remove(zp)
  except Exception as e: print('ZIP-HATA',z,e,flush=True)
  print(i+1,'/',len(zips),z,'eksik',len(eks),flush=True)
with open(os.path.join(G,'bekleyen.tsv.tmp'),'w',encoding='utf-8') as o:
  for k,q in eks.items(): o.write(f'{k}\t{q}\n')
os.replace(os.path.join(G,'bekleyen.tsv.tmp'),os.path.join(G,'bekleyen.tsv'))
print('SAYFA',sayfa,'GORSEL',len(hepsi),'INDIRILMIS',len(hepsi&done),'EKSIK',len(eks),'3+HATALI',sum(1 for k in eks if bad[k]>=3))
for (a,b),n in sorted(tur.items(),key=lambda x:-x[1]): print('  ',a,b,n)
