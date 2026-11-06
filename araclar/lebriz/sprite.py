"""Önizlemeleri 16x16 hücrelik JPEG paftalara toplar. Kullanım: sprite.py <site_dizini> <onizleme_dizini>
Çıktı: <onizleme>/pafta/p-NNN.jpg ve <onizleme>/o-<kova>.json (anahtar -> [pafta_no, hücre, en, boy])."""
import os,sys,json,collections
from PIL import Image
S,O=sys.argv[1:3]; C=160; N=16
T=os.path.join(O,'k'); P=os.path.join(O,'pafta'); os.makedirs(P,exist_ok=True)
sira=[]
for f,p in (('sergiler.json','s'),('yazilar.json','y')):
  for a in sorted(json.load(open(os.path.join(S,f))),key=lambda a:a['id']):
    for g in a.get('eserler' if p=='s' else 'gorseller',[]):
      k=(g['yol'].strip('/')+'/'+g['kod']).strip('/')
      if os.path.exists(os.path.join(T,k.replace('/','__')+'.jpg')): sira.append((f'{p}-{a["id"]//100}',k))
kova=collections.defaultdict(dict); bas=0  # artımlı: eski atamalar korunur, yeni görseller yeni paftalara
for f in os.listdir(O):
  if f.startswith('o-') and f.endswith('.json'):
    kova[f[2:-5]]=json.load(open(os.path.join(O,f)))
eski={k for d in kova.values() for k in d}
if eski: bas=1+max(v[0] for d in kova.values() for v in d.values())
gor=set(eski); sira=[x for x in sira if not (x[1] in gor or gor.add(x[1]))]
for pn in range(0,len(sira),N*N):
  sp=Image.new('RGB',(C*N,C*((min(N*N,len(sira)-pn)+N-1)//N)),(236,235,230))
  for c,(kv,k) in enumerate(sira[pn:pn+N*N]):
    im=Image.open(os.path.join(T,k.replace('/','__')+'.jpg'))
    sp.paste(im,((c%N)*C+(C-im.width)//2,(c//N)*C+(C-im.height)//2))
    kova[kv][k]=[bas+pn//(N*N),c,im.width,im.height]
  sp.save(os.path.join(P,f'p-{bas+pn//(N*N):03d}.jpg'),'JPEG',quality=70,optimize=True)
for kv,d in kova.items(): json.dump(d,open(os.path.join(O,f'o-{kv}.json'),'w'),separators=(',',':'))
print('yeni pafta',(len(sira)+N*N-1)//(N*N),'ilk',bas,'yeni gorsel',len(sira),'kova',len(kova))
