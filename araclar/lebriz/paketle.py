#!/usr/bin/env python3
"""Lebriz koruma kopyasındaki tek tek dosyaları büyük zip paketlerine toplar (proje klasörü dosya sınırı).
Paketler koruma/ altında paket-<tur>-<zaman>-<n>.zip, dizin koruma/paketler.tsv (yol \t paket \t bayt).
Üye adı her zaman kanonik yoldur (düz ada düşmüş dosyalar da kanonik yola çevrilir).
Her paket önce yerelde kurulur, kaynakla bayt bayt doğrulanır, CRC ile sınanır, sonra WebDAV sunucusuna
(dav.py) 20 MB parçalar halinde yüklenip geri indirilerek sha256 ile doğrulanır; asıl dosyalar ancak bundan sonra
silinir. Zip proje deposuna yazılmaz (2026-11-05, depo kotası). Kaynak: proje klasörü + yerel hazırlık (paket.YEREL).
Kullanım: paketle.py <koruma> <yerel_gecici_dizin> [--sil]"""
import os,sys,glob,zipfile,time,shutil,re
K=os.path.abspath(sys.argv[1]); TMP=sys.argv[2]; SIL='--sil' in sys.argv
IDX=os.path.join(K,'paketler.tsv'); STAMP=time.strftime('%Y%m%d%H%M')
os.makedirs(TMP,exist_ok=True)
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from paket import kanonik,koklar; import dav
YD=os.path.join(K,'sunucu-dizini.tsv')
TURLER=[('sayfa','sayfalar/**/*.html.gz',150e6),('muzayede','muzayede/sayfalar/**/*.html.gz',150e6),('gorsel','gorseller/**/*.jpg',400e6)]
mevcut=set()
if os.path.exists(IDX):
  for l in open(IDX,encoding='utf-8'):
    a=l.rstrip('\n').split('\t')
    if a and a[0]: mevcut.add(a[0])
toplam_once=0; silinen=0
for tur,pat,lim in TURLER:
  fs=sorted((f,R) for R in koklar(K) for f in glob.glob(os.path.join(R,pat),recursive=True) if not f.endswith('.tmp'))
  ogeler=[]; gor=set()
  for f,R in fs:
    c=kanonik(os.path.relpath(f,R))
    if c in gor or c in mevcut: continue  # zaten pakette (önceki yarıda kalan tur) ya da aynı yol iki kez
    gor.add(c); ogeler.append((f,c))
  toplam_once+=len(fs)
  parca=[]; boy=0; n=0
  def yaz(parca,n):
    ad=f'paket-{tur}-{STAMP}-{n:03d}.zip'; yer=os.path.join(TMP,ad)
    with zipfile.ZipFile(yer,'w',zipfile.ZIP_STORED,allowZip64=True) as z:
      for f,c in parca: z.write(f,c)
    with zipfile.ZipFile(yer) as z:  # yerelde bayt bayt doğrula
      for f,c in parca:
        if z.read(c)!=open(f,'rb').read(): raise SystemExit(f'DOGRULAMA HATASI {ad} {c}')
    with zipfile.ZipFile(yer) as z:
      bad=z.testzip()
      if bad: raise SystemExit(f'CRC HATASI {ad} {bad}')
      if len(z.namelist())!=len(parca): raise SystemExit(f'SAYI HATASI {ad}')
    dav.yukle(yer,YD)  # yükle + geri indir + sha256; başarısızsa istisna, asıl dosyalar silinmez
    with open(IDX,'a',encoding='utf-8') as o:
      for f,c in parca: o.write(f'{c}\t{ad}\t{os.path.getsize(f)}\n')
    os.remove(yer)
    print(f'{time.strftime("%H:%M:%S")} {ad} {len(parca)} dosya dogrulandi, sunucuya yuklendi',flush=True)
    return ad
  for f,c in ogeler:
    parca.append((f,c)); boy+=os.path.getsize(f)
    if boy>=lim: n+=1; yaz(parca,n); parca=[]; boy=0
  if parca: n+=1; yaz(parca,n)
  if SIL:
    for f,R in fs:
      for dene in range(3):
        try: os.remove(f); silinen+=1; break
        except FileNotFoundError: break
        except OSError: time.sleep(2)  # ağ klasörü ara sıra G/Ç hatası veriyor; kalan bir sonraki turda silinir
    print(f'{tur}: {len(fs)} asil dosya silindi',flush=True)
if SIL:  # boş klasörleri kaldır
  for R in koklar(K):
   for kok in ['sayfalar','muzayede/sayfalar','gorseller']:
    for d,_,_ in sorted(os.walk(os.path.join(R,kok),onerror=lambda e:None),key=lambda x:-len(x[0])):
      if d.rstrip('/')!=os.path.join(R,kok).rstrip('/'):
        try: os.rmdir(d)
        except OSError: pass
print(f'BITTI once={toplam_once} silinen={silinen}',flush=True)
