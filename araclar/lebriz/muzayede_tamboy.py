"""Müzayede bankası görsellerinin büyük boyları, paket dosyalarında. Kullanım: muzayede_tamboy.py <koruma> <cikti>
Ortam: BOY (uzun kenar, varsayılan 1024), KALITE (72), PAKET_MB (100).
Çıktı: <cikti>/t-NNN.bin (JPEG'ler art arda) ve <cikti>/tam-harita.json (anahtar -> [paket, ofset, bayt, en, boy]).
Sayfa görseli files.read(yol, {offset, length}) ile tek okumada alır. Artımlı: haritadaki anahtarlar atlanır."""
import os,sys,io,json,zipfile,collections
from PIL import Image
sys.path.insert(0,'/mnt/project-files/arastirma/sanat-tarihi/lebriz/araclar'); import paket
K,O=sys.argv[1:3]; M=int(os.environ.get('BOY','1024')); Q=int(os.environ.get('KALITE','72'))
PB=int(os.environ.get('PAKET_MB','100'))*1024*1024
os.makedirs(O,exist_ok=True); HP=os.path.join(O,'tam-harita.json')
har=json.load(open(HP)) if os.path.exists(HP) else {}
def key(r): return r[len('gorseller/'):-4]
zips=collections.defaultdict(list)
for r,z in paket.dizin(K).items():
  if r.startswith('gorseller/muzdb/') and r.endswith('.jpg') and key(r) not in har: zips[z].append(r)
print('eksik',sum(map(len,zips.values())),'zip',len(zips),flush=True)
pn=max((v[0] for v in har.values()),default=0)
def ppath(n): return os.path.join(O,f't-{n:03d}.bin')
out=open(ppath(pn),'ab')
for i,(z,rs) in enumerate(sorted(zips.items())):
  try:
    zp=paket.zip_yolu(K,z)
    with zipfile.ZipFile(zp) as zf:
      for r in sorted(rs):
        try:
          im=Image.open(io.BytesIO(zf.read(r))); im.draft('RGB',(M,M)); im=im.convert('RGB'); im.thumbnail((M,M))
          b=io.BytesIO(); im.save(b,'JPEG',quality=Q,optimize=True,progressive=True); b=b.getvalue()
          if out.tell()+len(b)>PB: out.close(); pn+=1; out=open(ppath(pn),'ab')
          off=out.tell(); out.write(b); har[key(r)]=[pn,off,len(b),im.width,im.height]
        except Exception as e: print('HATA',r,e,flush=True)
    out.flush(); json.dump(har,open(HP+'.tmp','w'),separators=(',',':')); os.replace(HP+'.tmp',HP)
    paket._Z.pop(z,None)
    if zp.startswith(paket.ONBELLEK): os.remove(zp)
  except Exception as e: print('ZIP-HATA',z,e,flush=True)
  print(i+1,'/',len(zips),z,len(rs),'toplam',len(har),flush=True)
out.close(); print('BITTI',len(har),'paket',pn+1,flush=True)
