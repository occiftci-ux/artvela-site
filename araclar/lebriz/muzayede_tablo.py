"""Lebriz müzayede bankası sayfalarından kayıt tablosu. Kullanım: muzayede_tablo.py <koruma> <cikti_dizini>
Çıktı: kayitlar.tsv (her lot bir satır) ve sanatcilar.tsv."""
import os,sys,re,gzip,html,csv
sys.path.insert(0,'/mnt/project-files/arastirma/sanat-tarihi/lebriz/araclar'); import paket
K,O=sys.argv[1:3]
def oku(i,p):
  for r in (f'muzayede/sayfalar/{int(i)%100:02d}/{i}-{p}.html.gz',f'muzayede/sayfalar/{int(i)%100}/{i}-{p}.html.gz',f'muzayede/sayfalar/{i}-{p}.html.gz'):
    try: return gzip.decompress(paket.oku(K,r)).decode('utf-8','ignore')
    except Exception: pass
def temiz(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
man={}
for l in open(os.path.join(K,'muzayede/manifest.tsv'),encoding='utf-8'):
  f=l.rstrip('\n').split('\t')
  if len(f)>=4 and f[3]=='tamam': man[f[1]]=int(f[2])
adlar={}
try:
  for r in csv.reader(open(os.path.join(K,'muzayede-sanatci-listesi.csv'),encoding='utf-8')):
    if r and r[0].isdigit(): adlar[r[0]]=r[1]
except Exception: pass
ALAN=['sanatci_id','sanatci','lot','muzayede_evi','tarih','olcu','teknik','eser_yili','ozellik','acilis_trl','satis_trl','acilis_usd','satis_usd','acilis_eur','satis_eur','gorsel']
w=open(os.path.join(O,'kayitlar.tsv'),'w',encoding='utf-8'); w.write('\t'.join(ALAN)+'\n')
eksik=0; n=0
for j,(i,np) in enumerate(sorted(man.items(),key=lambda x:int(x[0]))):
  for p in range(1,np+1):
    t=oku(i,p)
    if t is None: eksik+=1; open(os.path.join(O,'eksik.txt'),'a').write(f'{i}\t{p}\n'); continue
    for r in re.split(r'id="aucDB_awv_lstThumbs_ctl\d+_awd_pnl1"',t)[1:]:
      d={}
      for a,b in re.findall(r'_fld(\w+)"[^>]*>(.*?)</(?:td|span)>',r,re.S):
        v=temiz(b)
        if not v:  # satış fiyatları metin değil, title'ı fiyat olan resim olarak geliyor
          m2=re.search(r'title="([\d.,]+)',b); v=m2.group(1) if m2 else ''
        d[a]=v
      if 'Auction' not in d: continue
      lot=re.search(r'_lblLotNo"[^>]*>(.*?)</span>',r,re.S); lot=temiz(lot.group(1)).replace('Lot No:','').strip() if lot else ''
      a=d.get('Auction',''); ev,tarih=(a.rsplit(' - ',1)+[''])[:2] if ' - ' in a else (a,'')
      m=re.match(r'(\d\d)\.(\d\d)\.(\d\d)$',tarih.strip())
      if m: yy=int(m.group(3)); tarih=f'{1900+yy if yy>30 else 2000+yy}-{m.group(2)}-{m.group(1)}'
      oz=d.get('Specs','').replace('Özellikler:','').strip(); par=[x.strip() for x in oz.split(' - ')]
      olcu=par[0] if par and re.search(r'\d.*(cm|mm)',par[0]) else ''
      kalan=par[1:] if olcu else par
      yil=kalan[-1] if kalan and re.fullmatch(r'(c\.?\s*)?\d{4}(\s*-\s*\d{4})?s?',kalan[-1]) else ''
      teknik=' - '.join(kalan[:-1] if yil else kalan)
      g=re.search(r'iName=([^&"]+)&amp;iPath=([^&"]+)',r); gor=(g.group(2).strip('/')+'/'+g.group(1)) if g else ''
      sat=[i,d.get('Sanatci') or adlar.get(i,''),lot,ev.strip(),tarih.strip(),olcu,teknik,yil,oz]+[d.get(k,'') for k in ('PriceOpeningTRL','PriceSaleTRL','PriceOpeningUSD','PriceSaleUSD','PriceOpeningEUR','PriceSaleEUR')]+[gor]
      w.write('\t'.join(x.replace('\t',' ') for x in sat)+'\n'); n+=1
  if j%500==0: print(j,len(man),'kayit',n,flush=True)
w.close(); print('BITTI kayit',n,'eksik_sayfa',eksik,flush=True)
