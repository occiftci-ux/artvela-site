#!/usr/bin/env python3
"""Lebriz görsellerinin koruma kopyası (lebrizImages.net). Kaydedilmiş sayfalardaki imageHandler
bağlantılarını bulur, her görseli en büyük boyutta (iResizeAmount=3000 → ~1280px) indirir.
Kullanım: gorsel_cek.py <koruma_dizini> <saat>   (DELAY ortam değişkeni)"""
import os,re,sys,time,gzip,glob,random,html,urllib.request,urllib.parse,http.cookiejar
ROOT=sys.argv[1]; MAXH=float(sys.argv[2]); DELAY=float(os.environ.get('DELAY','1.0'))
G=os.path.join(ROOT,'gorseller'); os.makedirs(G,exist_ok=True)
MAN=os.path.join(G,'manifest.tsv'); TAR=os.path.join(G,'taranan.txt'); ERR=os.path.join(G,'hatalar.tsv')
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import paket  # klasör + zip paketleri
UA={'User-Agent':'ArtvelaArsivKoruma/1.0 (arastirma; yavas tarama)'}
cj=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
IMG=re.compile(r'imageHandler\.ashx\?([^"\'\s>]+)')
def key(q): return (q.get('iPath','').strip('/')+'/'+q.get('iName','')).strip('/')
done=set(); bad={}
if os.path.exists(MAN):
  for l in open(MAN,encoding='utf-8'):
    f=l.rstrip('\n').split('\t')
    if len(f)>=2: done.add(f[1])
if os.path.exists(ERR):
  for l in open(ERR,encoding='utf-8'):
    f=l.split('\t')
    if len(f)>1 and 'Input/output' not in l: bad[f[1]]=bad.get(f[1],0)+1
done|={r[10:-4] for r in paket.dizin(ROOT) if r.startswith('gorseller/') and r.endswith('.jpg')}  # paketteki görseller de indirilmiş sayılır
scanned=set(open(TAR,encoding='utf-8').read().split('\n')) if os.path.exists(TAR) else set()
end=time.time()+MAXH*3600; n=0
BEK=os.path.join(G,'bekleyen.tsv')  # kalıcı kuyruk: tur bitince kalanlar kaybolmasın (11 Kasım hatası)
def bekleyen():
  q=[]
  if os.path.exists(BEK):
    for l in open(BEK,encoding='utf-8'):
      a=l.rstrip('\n').split('\t')
      if len(a)==2 and a[0] not in done and bad.get(a[0],0)<3: q.append((a[0],dict(urllib.parse.parse_qsl(a[1],keep_blank_values=True))))
  return q
def scan():
  """Yeni sayfaları tara; öncelik: dergi/sergi sayfaları, sonra müzayede."""
  q=[]; bek=open(BEK,'a',encoding='utf-8')
  paketli=sorted(paket.dizin(ROOT))
  for pat,on in [('sayfalar/*/*.html.gz','sayfalar/'),('sayfalar/*.html.gz',None),('muzayede/sayfalar/*/*.html.gz','muzayede/'),('muzayede/sayfalar/*.html.gz',None)]:
    new=[(f,R) for R in paket.koklar(ROOT) for f in glob.glob(os.path.join(R,pat)) if f not in scanned]  # proje + yerel hazırlık
    if on: new+=[(os.path.join(ROOT,r),ROOT) for r in paketli if r.startswith(on) and r.endswith('.html.gz') and os.path.join(ROOT,r) not in scanned]
    for f,R in new:
      try: t=gzip.decompress(paket.oku(ROOT,paket.kanonik(os.path.relpath(f,R)))).decode('utf-8','ignore')
      except Exception: continue
      for m in IMG.finditer(t):
        p=dict(urllib.parse.parse_qsl(html.unescape(m.group(1))))
        if not p.get('iName'): continue
        k=key(p)
        if k not in done and bad.get(k,0)<3: q.append((k,p)); bek.write(f'{k}\t{urllib.parse.urlencode(p)}\n')
      bek.flush(); scanned.add(f); open(TAR,'a',encoding='utf-8').write(f+'\n')
      if len(q)>3000: return q
  return q
ilk=True
while time.time()<end:
  q=bekleyen() if ilk else []; ilk=False
  if not q: q=scan()
  seen=set()
  if not q: time.sleep(120); continue
  for k,p in q:
    if time.time()>end: break
    if k in done or k in seen: continue
    seen.add(k)
    p2=dict(p); p2['iResizeAmount']='3000'; p2['iResizeParam']='0'; p2['iSize']='0'; p2['watermark']=''
    url='http://lebrizImages.net/imageHandler.ashx?'+urllib.parse.urlencode(p2)
    time.sleep(DELAY+random.random())
    try:
      r=op.open(urllib.request.Request(url,headers=UA),timeout=180); b=r.read(); ct=r.headers.get('Content-Type','')
      if not ct.startswith('image/'): raise ValueError('görsel değil: '+ct)
      f=paket.yaz_yolu(ROOT,'gorseller/'+k+'.jpg')  # klasör açılamazsa düz ad
      open(f+'.tmp','wb').write(b); os.replace(f+'.tmp',f)
      open(MAN,'a',encoding='utf-8').write(f'{time.strftime("%Y-%m-%dT%H:%M:%S")}\t{k}\t{len(b)}\t{p.get("wType","")}\t{p.get("wID","")}\n'); done.add(k); n+=1
      if n%200==0: print(f'{time.strftime("%H:%M:%S")} gorsel={n} toplam={len(done)}',flush=True)
    except Exception as e:
      if 'Input/output' not in str(e): bad[k]=bad.get(k,0)+1
      open(ERR,'a',encoding='utf-8').write(f'{time.strftime("%Y-%m-%dT%H:%M:%S")}\t{k}\t{type(e).__name__}: {str(e)[:100]}\n'); time.sleep(5)
print(f'BITTI gorsel={n} toplam={len(done)}',flush=True)
