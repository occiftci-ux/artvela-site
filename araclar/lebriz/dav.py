"""Lebriz WebDAV deposu (Onur'un sunucusu, https://ocal.galeribej.com/lebriz-depo/).
Şifre yalnız ortam sırrından (ONUR_SUNUCU_ANAHTAR) okunur, hiçbir dosyaya yazılmaz; curl'e stdin ile verilir.
Yerleşim: /lebriz-depo/koruma/<zip>/<zip>.partNNN (20 MB, Cloudflare 100 sn sınırı), dizin /lebriz-depo/sunucu-dizini.tsv
(dosya, toplam_bayt, sha256, parca_sayisi, parca, parca_bayt, parca_sha256, uzak_yol, tarih)."""
import os,subprocess,hashlib,time,tempfile,concurrent.futures as cf
DAV='https://ocal.galeribej.com/lebriz-depo'; KULLANICI='ocal-lebriz'; PARCA=20*1024*1024; PARALEL=4
BASLIK='dosya\ttoplam_bayt\tsha256\tparca_sayisi\tparca\tparca_bayt\tparca_sha256\tuzak_yol\ttarih\n'
def _curl(args,veri=None):
  s=os.environ.get('ONUR_SUNUCU_ANAHTAR')
  if not s: raise RuntimeError('ONUR_SUNUCU_ANAHTAR ortam sırrı yok')
  cfg=f'user = "{KULLANICI}:{s}"\n'
  return subprocess.run(['curl','-sS','--fail','--retry','4','--retry-delay','5','-K','-']+args,input=cfg.encode(),capture_output=True,check=True).stdout
def _sha(p):
  h=hashlib.sha256()
  with open(p,'rb') as f:
    for b in iter(lambda:f.read(1<<20),b''): h.update(b)
  return h.hexdigest()
def dizin():
  """Sunucudaki dizin: {zip_adi: [(parca, bayt, sha, uzak_yol), ...], ...} ve zip sha'ları."""
  t=_curl([DAV+'/sunucu-dizini.tsv']).decode('utf-8')
  d={}; sha={}
  for l in t.splitlines()[1:]:
    a=l.split('\t')
    if len(a)<8: continue
    d.setdefault(a[0],[]).append((a[4],int(a[5]),a[6],a[7])); sha[a[0]]=(a[2],int(a[1]))
  for k in d: d[k].sort()
  return d,sha
def indir(ad,hedef):
  """Zip'i parçalarından birleştirip hedefe yazar; parça ve bütün sha256 doğrulanır."""
  d,sha=dizin()
  if ad not in d: raise FileNotFoundError(f'{ad} sunucu dizininde yok')
  tmp=hedef+'.tmp'; h=hashlib.sha256()
  with open(tmp,'wb') as o:
    for pa,pb,ps,yol in d[ad]:
      b=_curl(['https://ocal.galeribej.com'+yol])
      if len(b)!=pb or hashlib.sha256(b).hexdigest()!=ps: raise IOError(f'parça doğrulanamadı {pa}')
      o.write(b); h.update(b)
  if h.hexdigest()!=sha[ad][0]: raise IOError(f'birleşik sha tutmadı {ad}')
  os.replace(tmp,hedef); return hedef
def yukle(yol,yerel_dizin=None):
  """Yerel dosyayı parçalayıp yükler, her parçayı geri indirip doğrular, sunucu dizinine ekler.
  Başarılıysa True; dosya silinmez (silmek çağıranın işi)."""
  ad=os.path.basename(yol); boy=os.path.getsize(yol); sha=_sha(yol)
  tmpd=tempfile.mkdtemp(prefix='dav-'); parcalar=[]
  with open(yol,'rb') as f:
    i=0
    while True:
      b=f.read(PARCA)
      if not b: break
      p=os.path.join(tmpd,f'{ad}.part{i:03d}'); open(p,'wb').write(b); parcalar.append(p); i+=1
  try: _curl(['-o','/dev/null','-X','MKCOL',f'{DAV}/koruma/{ad}/'])
  except subprocess.CalledProcessError: pass
  def bir(p):
    pa=os.path.basename(p); ps=_sha(p); u=f'{DAV}/koruma/{ad}/{pa}'
    for _ in range(3):
      try:
        _curl(['-o','/dev/null','-T',p,u])
        if hashlib.sha256(_curl([u])).hexdigest()==ps: return (pa,os.path.getsize(p),ps,f'/lebriz-depo/koruma/{ad}/{pa}')
      except subprocess.CalledProcessError: pass
      time.sleep(10)
    raise IOError(f'yüklenemedi {pa}')
  try:
    with cf.ThreadPoolExecutor(PARALEL) as ex: sonuc=list(ex.map(bir,parcalar))
  finally:
    for p in parcalar: os.remove(p)
    os.rmdir(tmpd)
  t=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
  satir=''.join(f'{ad}\t{boy}\t{sha}\t{len(sonuc)}\t{pa}\t{pb}\t{ps}\t{u}\t{t}\n' for pa,pb,ps,u in sonuc)
  try: eski=_curl([DAV+'/sunucu-dizini.tsv']).decode('utf-8')
  except subprocess.CalledProcessError: eski=BASLIK
  yeni=eski+satir
  with tempfile.NamedTemporaryFile('w',delete=False,encoding='utf-8') as o: o.write(yeni)
  _curl(['-o','/dev/null','-T',o.name,DAV+'/sunucu-dizini.tsv'])
  if yerel_dizin:  # proje deposunda küçük kopya
    open(yerel_dizin+'.tmp','w',encoding='utf-8').write(yeni); os.replace(yerel_dizin+'.tmp',yerel_dizin)
  os.remove(o.name); return True
