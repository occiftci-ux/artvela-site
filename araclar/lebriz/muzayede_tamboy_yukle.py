"""Müzayede bankası görsellerinin asıl (tam boy, ~1280 px) dosyalarını Onur'un sunucusuna tek tek koyar,
özel tablodaki "Tam boy" bağlantısı için. Kullanım: muzayede_tamboy_yukle.py <koruma> <kayit_dosyasi>
Uzak yerleşim: /lebriz-depo/tamboy/muzdb/NNNN/KNNNN-MMM.jpg. Asıllar zip'lerde kalır (silinmez).
Her yükleme HEAD ile boyutu kontrol edilerek doğrulanır; doğrulanan anahtar kayıt dosyasına yazılır (artımlı).
Ortam: PARALEL (8). Şifre yalnız ortam sırrından (dav.py)."""
import os,sys,zipfile,collections,tempfile,re,concurrent.futures as cf
sys.path.insert(0,'/mnt/project-files/arastirma/sanat-tarihi/lebriz/araclar'); import paket,dav
K,KAYIT=sys.argv[1:3]; PAR=int(os.environ.get('PARALEL','8')); D=dav.DAV+'/tamboy'
done=set(open(KAYIT).read().split()) if os.path.exists(KAYIT) else set()
zips=collections.defaultdict(list)
for r,z in paket.dizin(K).items():
  if r.startswith('gorseller/muzdb/') and r.endswith('.jpg') and r[len('gorseller/'):-4] not in done: zips[z].append(r)
print('eksik',sum(map(len,zips.values())),'zip',len(zips),flush=True)
def mk(u):
  try: dav._curl(['-o','/dev/null','-X','MKCOL',u])
  except Exception: pass
mk(D+'/'); mk(D+'/muzdb/'); dirs=set()
tmpd=tempfile.mkdtemp(prefix='tamboy-')
def bir(r,b):
  k=r[len('gorseller/'):-4]; u=f'{D}/{k}.jpg'; p=os.path.join(tmpd,k.replace('/','__')+'.jpg'); open(p,'wb').write(b)
  try:
    for _ in range(3):
      try:
        dav._curl(['-o','/dev/null','-T',p,u])
        h=dav._curl(['-I',u]).decode('latin-1')
        m=re.findall(r'content-length:\s*(\d+)',h,re.I)
        if m and int(m[-1])==len(b): return k
      except Exception: pass
    return None
  finally: os.remove(p)
log=open(KAYIT,'a'); n=0; hata=0
for i,(z,rs) in enumerate(sorted(zips.items())):
  try:
    zp=paket.zip_yolu(K,z)
    with zipfile.ZipFile(zp) as zf, cf.ThreadPoolExecutor(PAR) as ex:
      for d in sorted({os.path.dirname(r[len('gorseller/'):]) for r in rs}-dirs): mk(f'{D}/{d}/'); dirs.add(d)
      fs=[ex.submit(bir,r,zf.read(r)) for r in rs]
      for f in cf.as_completed(fs):
        k=f.result()
        if k: log.write(k+'\n'); n+=1
        else: hata+=1
    log.flush(); paket._Z.pop(z,None)
    if zp.startswith(paket.ONBELLEK): os.remove(zp)
  except Exception as e: print('ZIP-HATA',z,e,flush=True)
  print(i+1,'/',len(zips),z,len(rs),'yuklenen',n,'hata',hata,flush=True)
print('BITTI yuklenen',n,'hata',hata,flush=True)
