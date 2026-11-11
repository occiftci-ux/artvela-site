"""Müzayede bankası görsellerinden 96 px önizleme paftaları (16x16 hücre). Kullanım: muzayede_onizleme.py <koruma> <cikti>
Çıktı: <cikti>/pafta/m-NNN.jpg ve <cikti>/gorsel-harita.json (anahtar -> [pafta, hücre, en, boy]). Artımlı."""
import os,sys,io,json,zipfile,collections
from PIL import Image
sys.path.insert(0,'/mnt/project-files/arastirma/sanat-tarihi/lebriz/araclar'); import paket
K,O=sys.argv[1:3]; C=int(os.environ.get("HUCRE","96")); N=int(os.environ.get("SIRA","16")); Q=int(os.environ.get("KALITE","68"))
T=os.path.join(O,'k'); P=os.path.join(O,'pafta'); os.makedirs(T,exist_ok=True); os.makedirs(P,exist_ok=True)
def tp(r): return os.path.join(T,r[len('gorseller/'):-4].replace('/','__')+'.jpg')
zips=collections.defaultdict(list); hepsi=[]
for r,z in paket.dizin(K).items():
  if r.startswith('gorseller/muzdb/') and r.endswith('.jpg'):
    hepsi.append(r)
    if not os.path.exists(tp(r)): zips[z].append(r)
print('gorsel',len(hepsi),'eksik',sum(map(len,zips.values())),'zip',len(zips),flush=True)
for i,(z,rs) in enumerate(sorted(zips.items())):
  try:
    zp=paket.zip_yolu(K,z)
    with zipfile.ZipFile(zp) as zf:
      for r in rs:
        try:
          im=Image.open(io.BytesIO(zf.read(r))); im.draft('RGB',(2*C,2*C)); im=im.convert('RGB'); im.thumbnail((C,C))
          b=io.BytesIO(); im.save(b,'JPEG',quality=90); open(tp(r),'wb').write(b.getvalue())
        except Exception as e: print('HATA',r,e,flush=True)
    paket._Z.pop(z,None)
    if zp.startswith(paket.ONBELLEK): os.remove(zp)
  except Exception as e: print('ZIP-HATA',z,e,flush=True)
  print(i+1,'/',len(zips),z,len(rs),flush=True)
HP=os.path.join(O,'gorsel-harita.json')
har=json.load(open(HP)) if os.path.exists(HP) else {}
bas=1+max((v[0] for v in har.values()),default=-1)
sira=sorted(r[len('gorseller/'):-4] for r in hepsi if r[len('gorseller/'):-4] not in har and os.path.exists(tp(r)))
for pn in range(0,len(sira),N*N):
  grp=sira[pn:pn+N*N]
  sp=Image.new('RGB',(C*N,C*((len(grp)+N-1)//N)),(236,235,230))
  for c,k in enumerate(grp):
    im=Image.open(os.path.join(T,k.replace('/','__')+'.jpg'))
    sp.paste(im,((c%N)*C+(C-im.width)//2,(c//N)*C+(C-im.height)//2))
    har[k]=[bas+pn//(N*N),c,im.width,im.height]
  sp.save(os.path.join(P,f'm-{bas+pn//(N*N):03d}.jpg'),'JPEG',quality=Q,optimize=True,progressive=True)
json.dump(har,open(HP,'w'),separators=(',',':'))
print('BITTI yeni pafta',(len(sira)+N*N-1)//(N*N),'ilk',bas,'yeni',len(sira),'toplam',len(har),flush=True)
