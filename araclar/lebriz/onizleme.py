"""Lebriz sergi/yazı görselleri için küçük önizlemeler (160 px, JPEG q60). Kullanım: onizleme.py <koruma> <site_dizini> <cikti>"""
import os,sys,json,io,base64,collections,zipfile
from PIL import Image
K,S,O=sys.argv[1:4]
sys.path.insert(0,'/mnt/project-files/arastirma/sanat-tarihi/lebriz/araclar'); import paket
T=os.path.join(O,'k'); os.makedirs(T,exist_ok=True)
gerek={}  # paket yolu -> (kova adi, anahtar)
for f,p in (('sergiler.json','s'),('yazilar.json','y')):
  for a in json.load(open(os.path.join(S,f))):
    for g in a.get('eserler' if p=='s' else 'gorseller',[]):
      k=(g['yol'].strip('/')+'/'+g['kod']).strip('/')
      gerek['gorseller/'+k+'.jpg']=(f'{p}-{a["id"]//100}',k)
def tp(k): return os.path.join(T,k.replace('/','__')+'.jpg')
zips=collections.defaultdict(list)
for r,z in paket.dizin(K).items():
  if r in gerek and not os.path.exists(tp(gerek[r][1])): zips[z].append(r)
print('gerekli',len(gerek),'eksik',sum(map(len,zips.values())),'zip',len(zips),flush=True)
for i,(z,rs) in enumerate(sorted(zips.items())):
  zp=paket.zip_yolu(K,z)
  with zipfile.ZipFile(zp) as zf:
    for r in rs:
      try:
        im=Image.open(io.BytesIO(zf.read(r))); im.draft('RGB',(320,320)); im=im.convert('RGB'); im.thumbnail((160,160))
        b=io.BytesIO(); im.save(b,'JPEG',quality=60,optimize=True); open(tp(gerek[r][1]),'wb').write(b.getvalue())
      except Exception as e: print('HATA',r,e,flush=True)
  paket._Z.pop(z,None)
  if zp.startswith(paket.ONBELLEK): os.remove(zp)
  print(i+1,'/',len(zips),z,len(rs),flush=True)
kova=collections.defaultdict(dict)
for r,(kv,k) in gerek.items():
  p=tp(k)
  if os.path.exists(p): kova[kv][k]='data:image/jpeg;base64,'+base64.b64encode(open(p,'rb').read()).decode()
P=os.path.join(O,'paket'); os.makedirs(P,exist_ok=True)
for kv,d in kova.items(): json.dump(d,open(os.path.join(P,f'o-{kv}.json'),'w'),separators=(',',':'))
print('BITTI kova',len(kova),'gorsel',sum(map(len,kova.values())),flush=True)
