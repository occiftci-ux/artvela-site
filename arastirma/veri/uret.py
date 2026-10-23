# sanatcilar_veri.py'den sanatçı dosyalarını, CSV veritabanını ve dizini üretir.
# Kullanım: python3 arastirma/veri/uret.py
import csv
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
from sanatcilar_veri import SANATCILAR  # noqa: E402

KOK = os.path.dirname(BURASI)
# Sahiplik (koordinasyon/README.md §3): Artvela künyesi bulten/envanter.csv'den, emsal fiyatlar bulten/emsal-fiyatlar.csv'den okunur.
BULTEN = os.path.join(os.path.dirname(KOK), "bulten")
if not os.path.isdir(BULTEN):
    BULTEN = "/mnt/project-files/bulten"


def csv_oku(ad):
    yol = os.path.join(BULTEN, ad)
    if not os.path.exists(yol):
        return []
    with open(yol, newline="") as f:
        return list(csv.DictReader(f))


ENVANTER = {}
for r in csv_oku("envanter.csv"):
    ENVANTER.setdefault(r["slug"], []).append(r["artvela_kunye"] + (f" · {r['artvela_fiyat_TL']} TL" if r.get("artvela_fiyat_TL") else ""))
EMSAL = {}
for r in csv_oku("emsal-fiyatlar.csv"):
    if r.get("dogrulandi") == "evet":
        EMSAL.setdefault(r["slug"], []).append(r)
TARIH = "2026-10-23"

OLCUTLER = [
    ("A", "Eğitim ve akademik geçerlilik", [("a1", "Akademi / fakülte mezunu", 8), ("a2", "Yurtdışı eğitim, burs, rezidans", 4), ("a3", "Akademisyenlik, öğrenci yetiştirme", 3)]),
    ("B", "Sergi geçmişi", [("b1", "Kişisel sergiler", 10), ("b2", "Retrospektif / müze ve kurum sergisi", 8), ("b3", "Uluslararası sergi, salon, bienal, fuar", 7)]),
    ("C", "Kurumsal tanınırlık", [("c1", "Türkiye'deki müze koleksiyonları", 8), ("c2", "Yurtdışındaki müze koleksiyonları", 7), ("c3", "Ödüller", 5)]),
    ("D", "Sanat tarihindeki konum", [("d1", "Grup / akım kurucusu, kuşak temsilcisi", 8), ("d2", "Akademik yayın, tez, monografi, müze", 7)]),
    ("E", "Piyasa görünürlüğü", [("e1", "Türk müzayedeleri", 8), ("e2", "Uluslararası müzayedeler", 7), ("e3", "Fiyat seviyesi (doğrulanmış)", 6), ("e4", "Güncel galeri temsili", 4)]),
]
ALT_SAYISI = sum(len(alt) for _, _, alt in OLCUTLER)


def kademe(puan):
    for alt, ad in ((80, "I · Kanonik"), (60, "II · Yerleşik"), (40, "III · Güçlü orta"), (20, "IV · Gelişen")):
        if puan >= alt:
            return ad
    return "V · İzleme"


def cekic(r):
    rakam = "".join(c if c.isdigit() else " " for c in r.get("satis_fiyati", "")).split()
    return int(rakam[0]) if rakam else 0


def emsal_puani(s):
    # M-D001 (PUANLAMA.md §4.1): e1 ve e3 yalnız emsal-fiyatlar.csv dogrulandi=evet satırlarından türetilir; elle girilen puan daha yüksekse korunur.
    satirlar = EMSAL.get(s["slug"], [])
    if not satirlar:
        return
    p = s["puan"]
    evler = sorted({r["kaynak"] for r in satirlar})
    n = len(satirlar)
    e1 = 3 if n == 1 else 4 if n <= 3 else 5
    if len(evler) > 1:
        e1 = min(8, e1 + 2)
    if not p.get("e1") or p["e1"][0] < e1:
        p["e1"] = (e1, f"emsal: {n} lot, {', '.join(evler)}")
    satilan = [cekic(r) for r in satirlar if r.get("satildi_mi") == "evet" and cekic(r)]
    if satilan:
        en = max(satilan)
        e3 = 1 if en < 100000 else 2 if en < 250000 else 3 if en < 1000000 else 4
        if not p.get("e3") or p["e3"][0] < e3:
            tl = f"{en:,}".replace(",", ".")
            p["e3"] = (e3, f"emsal: {len(satilan)}/{n} lot satıldı, en yüksek çekiç {tl} TL")


def hesapla(s):
    p = s["puan"]
    toplam = sum(v[0] for v in p.values() if v)
    dolu = sum(1 for v in p.values() if v)
    boyut = {kod: sum(p[k][0] for k, _, _ in alt if p.get(k)) for kod, _, alt in OLCUTLER}
    kapsam = round(100 * dolu / ALT_SAYISI)
    kd = kademe(toplam)
    if kapsam < 70:
        kd = f"({kd}) ön puan"
    return toplam, kapsam, kd, boyut


def liste(xs, bos="Doğrulanacak."):
    return "\n".join(f"- {x}" for x in xs) if xs else f"- {bos}"


BEJ_OLCUTLERI = [
    ("nitelik", "İşin niteliği ve zanaat"), ("tutarlilik", "Dilin tutarlılığı ve özgünlüğü"),
    ("figur", "Figürle ilişki"), ("derinlik", "Düşünsel derinlik"),
    ("hacim", "Üretim hacmi ve kariyer niyeti"), ("bagimsizlik", "Piyasadan bağımsızlık"),
]


def bej_bolumu(s):
    # Galeri keşif kanalından gelen adaylar için (vizyon/galeri.md G-Y1, GO-001). Arşiv puanından ayrıdır.
    b = s.get("bej")
    if not b:
        return ""
    puanlar = b.get("puan", {})
    satir = "\n".join(f"| {ad} | {puanlar[k][0] if puanlar.get(k) else 0} / 10 | {puanlar[k][1] if puanlar.get(k) else '*eksik*'} |" for k, ad in BEJ_OLCUTLERI)
    toplam = sum(v[0] for v in puanlar.values() if v)
    notlar = "\n".join(f"- {n}" for n in b.get("notlar", []))
    return f"""## Bej Keşif Değerlendirmesi [G-Y1]

**Keşif kanalı:** {b.get('kanal', 'Doğrulanacak')}  
**Huni aşaması:** {b.get('huni', '1 · Radar')}

| Ölçüt | Puan | Gerekçe |
|---|---|---|
{satir}
| **Toplam** | **{toplam} / 60** | |

{notlar}

"""


def artvela_listesi(s):
    return ENVANTER.get(s["slug"]) or s["artvela"]


def emsal_tablosu(s):
    satirlar = EMSAL.get(s["slug"], [])
    if not satirlar:
        return "| | | | | | |\n\n*bulten/emsal-fiyatlar.csv'de bu sanatçı için doğrulanmış satış yok. Eksikse is-kaydi.csv'ye fiyat-emsal için istek satırı yazılır.*"
    return "\n".join(f"| {r['tarih']} | {r['kaynak']} {r['muzayede_lot']} | {r['eser']}, {r['yil']}, {r['teknik']}, {r['olcu_cm']} | {r['tahmini_deger']} | {r['satis_fiyati']} {r['para_birimi']} ({r['satildi_mi']}) | {r['kaynak_url']} |" for r in satirlar)


def dosya(s):
    toplam, kapsam, kd, boyut = hesapla(s)
    satirlar = []
    for kod, ad, alt in OLCUTLER:
        satirlar.append(f"| **{kod} · {ad}** | | **{boyut[kod]} / {sum(m for _, _, m in alt)}** | |")
        for k, etiket, mx in alt:
            v = s["puan"].get(k)
            satirlar.append(f"| {k} | {etiket} | {v[0] if v else 0} / {mx} | {v[1] if v else '*eksik*'} |")
    tablo = "\n".join(satirlar)
    alint = "\n\n".join(f"> {a}: {k}" for a, k in s["alintilar"]) or "> Henüz eklenmedi. Söyleşi, video ve sanatçının sosyal medyası taranacak."
    kaynak = "\n".join(f"{i}. [{i}] {k}" for i, k in enumerate(s["kaynaklar"], 1))
    bej = bej_bolumu(s)
    detay = f"\n> Ayrıntılı araştırma notu: [{s['detay']}]({s['detay']})\n" if s.get("detay") else ""
    return f"""---
sanatci: "{s['ad']}"
dogum: "{s['dogum']}"
olum: "{s['olum']}"
disiplin: "{s['disiplin']}"
kabul: "{s['kabul'].split(':')[0]}"
puan: {toplam}
kademe: "{kd}"
veri_kapsami: {kapsam}
son_guncelleme: "{TARIH}"
guven: "taslak"
---

# {s['ad']}
{detay}
| Puan | Kademe | Veri kapsamı | Kabul |
|---|---|---|---|
| **{toplam} / 100** | {kd} | %{kapsam} | {s['kabul']} |

## 1. Künye ve Biyografi

**Doğum / ölüm:** {s['dogum']}{' · ' + s['olum'] if s['olum'] else ''}
**Disiplin:** {s['disiplin']}

**Eğitim**
{liste(s['egitim'])}

**Kronoloji**
{liste(s['kronoloji'])}

## 2. Akım ve Sanat Tarihi Bağlamı

- **Akım / grup:** {s['akim']}
- **Temalar:** {s['temalar']}

## 3. Felsefi Bağlam

Doldurulacak. Merkez kavramlar, ilişkili düşünürler ve sanatçının kendi sözleri ([şablon](../SABLON-sanatci.md) bölüm 3).

## 4. Sanatçının Kendi Ağzından

{alint}

## 5. Eser Analizi (Artvela)

{liste(artvela_listesi(s), 'Henüz Artvela müzayedesinde yer almadı.')}

## 6. Kurumsal Kayıt ve Piyasa Verisi

**Müze ve kurum koleksiyonları**
{liste(s['koleksiyonlar'])}

**Ödüller**
{liste(s['oduller'], 'Kaynakta ödül bilgisi yok, doğrulanacak.')}

**Satış kayıtları** (kaynak: `bulten/emsal-fiyatlar.csv`, yalnız `dogrulandi=evet`)

| Tarih | Müzayede evi | Eser | Tahmin | Satış | Kaynak |
|---|---|---|---|---|---|
{emsal_tablosu(s)}

## 7. Puan Dökümü

Ölçütler için bkz. [PUANLAMA.md](../PUANLAMA.md). *Eksik* alt ölçütler kanıt gelene kadar 0 sayılır.

| Kod | Ölçüt | Puan | Kanıt |
|---|---|---|---|
{tablo}
| | **Toplam** | **{toplam} / 100** | Veri kapsamı %{kapsam} |

{bej}## 8. Kaynakça

{kaynak}

## 9. Açık Sorular

- [ ] *Eksik* işaretli alt ölçütler için kaynak bul.
- [ ] E2/E3: emsal dosyasında doğrulanmış satır yoksa is-kaydi.csv'ye fiyat-emsal için istek yaz (kendin arama yapma).
- [ ] Müze koleksiyonlarını kurum sayfalarından doğrula (C1, C2).
"""


def main():
    hedef = os.path.join(KOK, "sanatcilar")
    os.makedirs(hedef, exist_ok=True)
    satirlar = []
    for s in SANATCILAR:
        emsal_puani(s)
        toplam, kapsam, kd, boyut = hesapla(s)
        with open(os.path.join(hedef, f"{s['slug']}.md"), "w") as f:
            f.write(dosya(s))
        satirlar.append(dict(slug=s["slug"], sanatci=s["ad"], dogum=s["dogum"], olum=s["olum"], disiplin=s["disiplin"],
                             kabul=s["kabul"].split(":")[0], puan=toplam, kademe=kd, veri_kapsami=kapsam,
                             A=boyut["A"], B=boyut["B"], C=boyut["C"], D=boyut["D"], E=boyut["E"],
                             artvela="; ".join(artvela_listesi(s)),
                             bej_huni=(s.get("bej") or {}).get("huni", ""),
                             bej_puan=sum(v[0] for v in (s.get("bej") or {}).get("puan", {}).values() if v) if s.get("bej") else "",
                             son_guncelleme=TARIH))
    satirlar.sort(key=lambda r: -r["puan"])
    with open(os.path.join(KOK, "sanatcilar.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(satirlar[0].keys()))
        w.writeheader()
        w.writerows(satirlar)
    tablo = "\n".join(
        f"| {i} | [{r['sanatci']}](sanatcilar/{r['slug']}.md) | {r['dogum']}{' – ' + r['olum'] if r['olum'] else ''} | **{r['puan']}** | {r['kademe']} | %{r['veri_kapsami']} | {r['A']} | {r['B']} | {r['C']} | {r['D']} | {r['E']} |"
        for i, r in enumerate(satirlar, 1))
    with open(os.path.join(KOK, "README.md"), "w") as f:
        f.write(f"""# Artvela Türk Sanatçılar Arşivi

Son güncelleme: {TARIH} · {len(satirlar)} sanatçı

- [PUANLAMA.md](PUANLAMA.md): kabul ölçütleri, 100 puanlık sistem, kademeler
- [SABLON-sanatci.md](SABLON-sanatci.md): ayrıntılı araştırma notu şablonu
- [sanatcilar.csv](sanatcilar.csv): veritabanı (Excel ya da Google Sheets ile açılır)
- `sanatcilar/`: her sanatçı için ayrı dosya
- `veri/`: ham veri (`sanatcilar_veri.py`) ve üretici (`uret.py`)

Puanlar **ön puandır**. Çoğu sanatçıda piyasa ve koleksiyon verisi henüz girilmedi, bu yüzden gerçek ağırlıklarının altında görünüyorlar. Kural için bkz. PUANLAMA.md §4.

| # | Sanatçı | Yaşam | Puan | Kademe | Veri | A /15 | B /25 | C /20 | D /15 | E /25 |
|---|---|---|---|---|---|---|---|---|---|---|
{tablo}
""")
    print(f"{len(satirlar)} sanatçı üretildi")


if __name__ == "__main__":
    main()
