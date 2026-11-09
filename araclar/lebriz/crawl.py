#!/usr/bin/env python3
"""Lebriz koruma kopyası: yavaş, tek bağlantılı, kaldığı yerden devam eden tarayıcı."""
import os,re,sys,time,gzip,hashlib,html,urllib.request,urllib.parse,collections,random,heapq,itertools,http.cookiejar
ROOT=sys.argv[1]            # .../lebriz/koruma
MAXH=float(sys.argv[2]) if len(sys.argv)>2 else 1.9   # saat
DELAY=float(os.environ.get('DELAY','2.5'))
BASE='http://lebriz.com/pages/'
PAGES=os.path.join(ROOT,'sayfalar')
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(ROOT)),'araclar')); import paket  # klasör + zip paketleri
MAN=os.path.join(ROOT,'manifest.tsv'); ERR=os.path.join(ROOT,'hatalar.tsv')
ALLOW=re.compile(r'^(lsd|exhibition|exhibitionList|artist|doc_View|gallery)\.aspx$',re.I)
SEEDS=['lsd.aspx?lang=TR','exhibitionList.aspx?listType=archive&lang=TR','exhibitionList.aspx?listType=current&lang=TR',
 'artist.aspx?lang=TR&listType=general&filterLetter=&filterType=-1&filterSearch=','doc_View.aspx?docID=143&pageID=21&lang=TR','doc_View.aspx?docID=60&pageID=22&lang=TR']
def norm(href,cur=BASE):
  href=href.strip().replace('&amp;','&')  # html.unescape '&sect' -> '§' yapıyordu
  if href.startswith(('javascript','mailto','#')): return None
  u=urllib.parse.urljoin(cur,href); p=urllib.parse.urlsplit(u)
  if p.netloc.lower() not in ('lebriz.com','www.lebriz.com'): return None
  path=p.path
  if not path.lower().startswith('/pages/'): return None
  name=path.split('/')[-1]
  if not ALLOW.match(name): return None
  q=urllib.parse.parse_qsl(p.query,keep_blank_values=True)
  d=dict(q)
  if d.get('lang','TR').upper()!='TR': return None
  d['lang']='TR'
  if name.lower()=='artist.aspx' and d.get('section')=='700': return None  # ziyaretçi defteri: kişisel veri, alınmaz
  if name.lower()=='artist.aspx' and d.get('exhID','0')!='0': d['exhID']='0'  # 2026-11-09: exhID yalnız geldiği sergiyi gösterir; aynı eser listesi her sergi için yeniden çekiliyordu
  if name.lower()=='artist.aspx' and (d.get('sortDir')=='ASC' or d.get('sortBy')=='retro'): return None  # 2026-11-09: aynı eser listesinin başka sıralaması; tek sıralama (generic DESC) yeter
  return name+'?'+urllib.parse.urlencode(sorted(d.items()))
def key(u): return hashlib.sha1(u.encode()).hexdigest()[:16]
def rel(u): k=key(u); return f'sayfalar/{k[:2]}/{k}.html.gz'
def pth(u): return os.path.join(ROOT,rel(u))
def oku(u): return gzip.decompress(paket.oku(ROOT,rel(u))).decode('utf-8','ignore')
LINK=re.compile(r'href\s*=\s*["\']([^"\']+)["\']',re.I)
def links(t): return {n for h in LINK.findall(t) if (n:=norm(h))}
done=set()
if os.path.exists(MAN):
  for l in open(MAN,encoding='utf-8'):
    f=l.rstrip('\n').split('\t')
    if len(f)>=2: done.add(f[1])
bad=collections.Counter()
if os.path.exists(ERR):
  for l in open(ERR,encoding='utf-8'):
    f=l.split('\t'); 
    if len(f)>1: bad[f[1]]+=1
# frontier'i kayıtlı sayfalardan yeniden kur
seen=set(done); front=[]; cnt=itertools.count()
def pri(u):
  if 'articleID=' in u and re.search(r'sectionID=3(&|$)',u): return 0
  for i,pat in enumerate(['exhID=','articleID=','artistID=','docID=','sectionID=','authorID=','galleryID='],1):
    if pat in u: return i
  return 9
def push(u,force=False):
  if u and (force or u not in seen) and bad[u]<3: seen.add(u); heapq.heappush(front,(pri(u),next(cnt),u))
for s in SEEDS: push(norm(s))
for s in sys.argv[3:]:
  for l in open(s):
    if l.strip(): push(norm(l.strip()))
for u in list(done):
  try: t=oku(u)
  except Exception: continue
  for n in links(t): push(n)
print(f'kayitli={len(done)} kuyruk={len(front)}',flush=True)

PMAN=os.path.join(ROOT,'sayfalama.tsv'); PMAN2=os.path.join(ROOT,'sayfalama2.tsv')
pdone=set()
if os.path.exists(PMAN):  # eski kayıt: sergi dışı ve 11'den az seçenekli olanlar tamam sayılır
  for l in open(PMAN,encoding='utf-8'):
    f=l.rstrip('\n').split('\t')
    if len(f)>=3 and not f[1].startswith('exhibition.aspx') and not re.search(r':1[1-9]|:[2-9]\d',f[2]): pdone.add(f[1])
if os.path.exists(PMAN2):
  for l in open(PMAN2,encoding='utf-8'):
    f=l.rstrip('\n').split('\t')
    if len(f)>=5 and f[4]=='tamam': pdone.add(f[1])
SEL=re.compile(r'<select[^>]*name="([^"]*\$pager1\$drpPage)"[^>]*>(.*?)</select>',re.S|re.I)
HID=re.compile(r'<input[^>]*type="hidden"[^>]*>',re.I)
def attr(tag,a):
  m=re.search(a+r'="([^"]*)"',tag); return html.unescape(m.group(1)) if m else ''
def formfields(t):
  d={}
  for tag in HID.findall(t):
    n=attr(tag,'name')
    if n: d[n]=attr(tag,'value')
  for m in re.finditer(r'<select[^>]*name="([^"]*)"[^>]*>(.*?)</select>',t,re.S|re.I):
    opts=re.findall(r'<option([^>]*)value="([^"]*)"',m.group(2))
    sel=[v for a,v in opts if 'selected' in a] or [v for a,v in opts]
    if sel: d[html.unescape(m.group(1))]=html.unescape(sel[0])
  return d
def total_of(t,pre,n):
  lid=pre.replace('$','_')+'_tdLabels1'
  m=re.search(r'id="'+re.escape(lid)+r'"[^>]*>(.*?)</td>',t,re.S)
  if m:
    mm=re.search(r'Sayfa\s*:\s*(\d+)\s*/\s*(\d+)',re.sub(r'<[^>]+>',' ',m.group(1)).replace('&nbsp;',' ').replace('&nbsp',' '))
    if mm: return int(mm.group(2))
  return n
def do_pagers(u,t):
  groups=[(m.group(1),len(re.findall(r'<option',m.group(2)))) for m in SEL.finditer(t)]
  tot=0; info=[]; ok=True
  for name,n in groups:
    pre=name[:-len('$drpPage')]; N=total_of(t,pre,n); info.append(f'{name}:{n}/{N}')
    if N<2: continue
    cur=t; tag=re.sub(r'[^A-Za-z0-9]+','-',pre).strip('-')
    cj=http.cookiejar.CookieJar(); o=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    for pg in range(2,N+1):
      d=formfields(cur); d[pre+'$butRight.x']='7'; d[pre+'$butRight.y']='7'
      got=None
      for att in range(3):
        time.sleep(DELAY+random.random()+att*5)
        try:
          got=o.open(urllib.request.Request(BASE+u,data=urllib.parse.urlencode(d).encode(),headers=UA),timeout=240).read().decode('utf-8',errors='ignore'); break
        except Exception as e:
          open(ERR,'a',encoding='utf-8').write(f'{time.strftime("%Y-%m-%dT%H:%M:%S")}\t{u}#{tag}-{pg}\t{type(e).__name__}: {str(e)[:120]}\n')
      if got is None: ok=False; break
      cur=got
      f=paket.yaz_yolu(ROOT,rel(u)[:-8]+f'.{tag}-{pg}.html.gz')
      with gzip.open(f+'.tmp','wt',encoding='utf-8') as g: g.write(cur)
      os.replace(f+'.tmp',f); tot+=1
  open(PMAN2,'a',encoding='utf-8').write(f'{time.strftime("%Y-%m-%dT%H:%M:%S")}\t{u}\t{";".join(info)}\t{tot}\t{"tamam" if ok else "eksik"}\n')
  if ok: pdone.add(u)
UA={'User-Agent':'ArtvelaArsivKoruma/1.0 (arastirma; yavas tarama)'}
end=time.time()+MAXH*3600; n=0
op=urllib.request.build_opener(urllib.request.ProxyHandler())
for u in [x for x in done if x not in pdone and norm(x)]:
  if time.time()>end: break
  try: do_pagers(u,oku(u))
  except Exception as e: print('pager-hata',u,e,flush=True)
print('sayfalama telafisi bitti',flush=True)
while front and time.time()<end:
  u=heapq.heappop(front)[2]; t0=time.time()
  try:
    r=op.open(urllib.request.Request(BASE+u,headers={'User-Agent':'ArtvelaArsivKoruma/1.0 (arastirma; yavas tarama)'}),timeout=240)
    b=r.read(); code=r.status
  except Exception as e:
    open(ERR,'a',encoding='utf-8').write(f'{time.strftime("%Y-%m-%dT%H:%M:%S")}\t{u}\t{type(e).__name__}: {str(e)[:120]}\n')
    bad[u]+=1
    if bad[u]<3: push(u,True)
    time.sleep(DELAY*4); continue
  t=b.decode('utf-8',errors='ignore')
  hedef=paket.yaz_yolu(ROOT,rel(u)); tmp=hedef+'.tmp'
  with gzip.open(tmp,'wb') as g: g.write(b)
  os.replace(tmp,hedef)
  m=re.search(r'<title>(.*?)</title>',t,re.S|re.I)
  open(MAN,'a',encoding='utf-8').write(f'{time.strftime("%Y-%m-%dT%H:%M:%S")}\t{u}\t{key(u)}\t{code}\t{len(b)}\t{html.unescape(m.group(1).strip()) if m else ""}\n'.replace('\r',' '))
  done.add(u); n+=1
  do_pagers(u,t)
  new=[x for x in links(t) if x not in seen]
  for x in new: push(x)
  if n%50==0: print(f'{time.strftime("%H:%M:%S")} indirilen={n} toplam={len(done)} kuyruk={len(front)} son={time.time()-t0:.1f}s',flush=True)
  time.sleep(DELAY+random.random())
print(f'BITTI indirilen={n} toplam={len(done)} kuyruk={len(front)}',flush=True)
