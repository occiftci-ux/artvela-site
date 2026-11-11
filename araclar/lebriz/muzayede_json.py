"""kayitlar.tsv + gorsel-harita.json -> site verisi. Kullanım: muzayede_json.py <muz_dizini> <site_veri_dizini>"""
import os,sys,csv,json,collections
M,V=sys.argv[1:3]; os.makedirs(V,exist_ok=True)
csv.field_size_limit(10**7)
R=list(csv.DictReader(open(os.path.join(M,'kayitlar.tsv'),encoding='utf-8'),delimiter='\t',quoting=csv.QUOTE_NONE))
H=json.load(open(os.path.join(M,'gorsel-harita.json'))) if os.path.exists(os.path.join(M,'gorsel-harita.json')) else {}
def n(x):
  x=x.replace(',','').replace('.','').strip()
  return int(x) if x.isdigit() else 0
evs=collections.Counter(r['muzayede_evi'] for r in R); EVL=[e for e,_ in evs.most_common()]; EI={e:i for i,e in enumerate(EVL)}
yr=collections.defaultdict(list)
san={}; kova=collections.defaultdict(lambda: collections.defaultdict(list))
for r in R:
  i=int(r['sanatci_id']); img=H.get(r['gorsel'],0)
  row=[r['lot'],EI[r['muzayede_evi']],r['tarih'],r['olcu'],r['teknik'],r['eser_yili']]+[n(r[k]) for k in ('acilis_trl','satis_trl','acilis_usd','satis_usd','acilis_eur','satis_eur')]+[img]
  kova[i//100][i].append(row)
  s=san.setdefault(i,[i,r['sanatci'],0,0]); s[2]+=1; s[3]+=1 if img else 0
  if r['tarih']: yr[r['muzayede_evi']].append(int(r['tarih'][:4]))
for b,d in kova.items(): json.dump(d,open(os.path.join(V,f'k-{b}.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
json.dump(sorted(san.values(),key=lambda s:-s[2]),open(os.path.join(V,'sanatcilar.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
json.dump([[e,evs[e],min(yr[e]) if yr[e] else 0,max(yr[e]) if yr[e] else 0] for e in EVL],open(os.path.join(V,'evler.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print('kayit',len(R),'sanatci',len(san),'ev',len(EVL),'kova',len(kova),'gorselli',sum(s[3] for s in san.values()))
