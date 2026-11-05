"""Lebriz koruma kopyası okuyucusu: bir dosyayı önce klasörde (kanonik ya da düz ad), yoksa zip paketlerinde arar.
Yollar koruma/ köküne göre kanonik yoldur: sayfalar/ab/<k>.html.gz, muzayede/sayfalar/NN/<id>-<pg>.html.gz,
gorseller/<iPath>/<iName>.jpg. Dizin: koruma/paketler.tsv (yol, paket, bayt).
2026-11-05: zip paketleri proje deposundan WebDAV sunucusuna taşındı (bkz. dav.py). Pakette olup klasörde
bulunmayan zip, sunucudan yerel önbelleğe (LEBRIZ_ONBELLEK, varsayılan ~/lebriz-onbellek) sha256 doğrulanarak indirilir.
Yeni çekilen tek tek dosyalar proje deposuna değil yerel hazırlık klasörüne (LEBRIZ_YEREL, varsayılan ~/lebriz-yerel)
yazılır; paketle.py bunları zip'leyip sunucuya yükler."""
import os,re,zipfile
_IDX={}; _Z={}
ONBELLEK=os.environ.get('LEBRIZ_ONBELLEK',os.path.expanduser('~/lebriz-onbellek'))
YEREL=os.environ.get('LEBRIZ_YEREL',os.path.expanduser('~/lebriz-yerel'))
def koklar(K):
  """Tek tek dosyaların aranacağı kökler: proje klasörü, sonra yerel hazırlık klasörü."""
  return [K]+([YEREL] if YEREL and os.path.abspath(YEREL)!=os.path.abspath(K) else [])
def zip_yolu(K,z):
  """Zip projede varsa onu, yoksa önbellekteki kopyayı (gerekirse sunucudan indirerek) verir."""
  p=os.path.join(K,z)
  if os.path.exists(p): return p
  c=os.path.join(ONBELLEK,z)
  if not os.path.exists(c):
    os.makedirs(ONBELLEK,exist_ok=True)
    import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import dav
    dav.indir(z,c)
  return c
def duz(rel):
  """Klasör açılamadığında kullanılan düz ad."""
  m=re.match(r'^sayfalar/[0-9a-f]{2}/(.+)$',rel)
  if m: return 'sayfalar/'+m.group(1)
  m=re.match(r'^muzayede/sayfalar/\d\d/(.+)$',rel)
  if m: return 'muzayede/sayfalar/'+m.group(1)
  if rel.startswith('gorseller/'): return 'gorseller/'+rel[10:].replace('/','__')
  return rel
def kanonik(rel):
  m=re.match(r'^sayfalar/([0-9a-f]{16}[^/]*)$',rel)
  if m: return f'sayfalar/{m.group(1)[:2]}/{m.group(1)}'
  m=re.match(r'^muzayede/sayfalar/(\d+)-(\d+\.html\.gz)$',rel)
  if m: return f'muzayede/sayfalar/{int(m.group(1))%100:02d}/{m.group(1)}-{m.group(2)}'
  m=re.match(r'^gorseller/([^/]+\.jpg)$',rel)
  if m and '__' in m.group(1): return 'gorseller/'+m.group(1).replace('__','/')
  return rel
def dizin(K):
  if K not in _IDX:
    d={}; f=os.path.join(K,'paketler.tsv')
    if os.path.exists(f):
      for l in open(f,encoding='utf-8'):
        a=l.rstrip('\n').split('\t')
        if len(a)>=2 and a[0]: d[a[0]]=a[1]
    _IDX[K]=d
  return _IDX[K]
def var(K,rel):
  return any(os.path.exists(os.path.join(R,rel)) or os.path.exists(os.path.join(R,duz(rel))) for R in koklar(K)) or rel in dizin(K)
def oku(K,rel):
  for R in koklar(K):
    for r in (rel,duz(rel)):
      p=os.path.join(R,r)
      if os.path.exists(p): return open(p,'rb').read()
  z=dizin(K).get(rel)
  if not z: raise FileNotFoundError(rel)
  if z not in _Z: _Z[z]=zipfile.ZipFile(zip_yolu(K,z))
  return _Z[z].read(rel)
def yaz_yolu(K,rel):
  """Yazılacak tam yol (yerel hazırlık klasöründe; LEBRIZ_YEREL boşsa proje klasöründe):
  klasör açılabiliyorsa kanonik, açılamıyorsa düz ad."""
  R=YEREL or K; p=os.path.join(R,rel)
  try: os.makedirs(os.path.dirname(p),exist_ok=True); return p
  except OSError: return os.path.join(R,duz(rel))
_PRE={}
def onekli(K,onek):
  """Kanonik yolu `onek` ile başlayan tüm kayıtlar (klasör + paket)."""
  if K not in _PRE:
    d={}
    for r in dizin(K): d.setdefault(r.rsplit('/',1)[0],[]).append(r)
    _PRE[K]=d
  kl=onek.rsplit('/',1)[0]
  out={r for r in _PRE[K].get(kl,[]) if r.startswith(onek)}
  for R in koklar(K):
    for r in (onek,duz(onek)):
      dd=os.path.join(R,os.path.dirname(r))
      if os.path.isdir(dd):
        b=os.path.basename(r)
        for f in os.listdir(dd):
          if f.startswith(b) and not f.endswith('.tmp'): out.add(kanonik(os.path.relpath(os.path.join(dd,f),R)))
  return sorted(out)
