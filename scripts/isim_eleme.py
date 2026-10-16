#!/usr/bin/env python3
"""Galeri isim havuzu: aday toplama ve gerekçeli eleme.

Kullanım: python3 scripts/isim_eleme.py
Çıktı:    docs/galeri/11-gece-calismasi/havuz.csv  (her aday, durum ve gerekçe)
          docs/galeri/11-gece-calismasi/eleme-ozeti.txt
"""
import csv
import glob
import re
from collections import OrderedDict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/galeri/11-gece-calismasi"

# Kullanıcının beğendiği referans isimler
BEGENILEN = ["Antre", "Radyal", "Bej", "Opak", "Meridyen", "Bediz"]

# ---------------------------------------------------------------------------
# 1. Gece turunda üretilen yeni aileler (Antre/Radyal çizgisi ağırlıklı)
# ---------------------------------------------------------------------------
YENI = {
    "Fransızca ödünç (mekân, kat, geçiş)": """
        Antresol Antrepo Etaj Etap Mezanin Parter Atik Fuaye Vestibül Lobi Arkad Portik Portal
        Atriyum Rotonda Belveder Veranda Kordon Peron Podyum Niş Kabin Gişe Vestiyer Esplanad
        Bulvar Avenü Pavyon Şale Şato Suit Budoar Korniş Panjur Paravan Abajur Avize Aplik
        Armatür Parke Karo Lavabo Komodin Konsol Tabure Gardırop Şantiye Hangar Antikamera
    """,
    "Fransızca ödünç (yüzey, doku, kumaş)": """
        Ajur Velur Vual Muare Lame Krep Şifon Organze Gipür Brode Plise Drape Gofre Satine Glase
        Masif Maroken Brokar Gobelen Fular Eşarp Kloş Volan Jarse Trikotaj Makrome Kurdele
        Bandrol Düble Apre Emaye Lake Vernik Patine Metalik Mat Brüt Bej Ekru Füme Opak Gri
        Nötr Degrade Nüans Pastel Krem Bordo Lila Antrasit
    """,
    "Fransızca ödünç (atölye, baskı, yayın)": """
        Ekol Tiraj Fasikül Etalaj Fiksatif Guaj Estamp Gravür Filigran Kalk Klişe Kuşe Gramaj
        Ozalit Paspartu Kartuş Vinyet Bordür Rozet Plaket Medalyon Biblo Maket Şablon Gabari
        Kalibre Repertuvar Albüm Portfolyo Dosya Arşiv Envanter Katalog Broşür Afiş Bülten
        Edisyon Versiyon Replik Rötuş Rölöve Kroki Eskiz Etüt Esans Kaşe Paraf Viza Vize
        Etiket Monogram Amblem Arma
    """,
    "Fransızca ödünç (sahne, zaman, hareket)": """
        Debü Antrakt Avan Prömiyer Repriz Bis Final Turne Prova Jest Rande Matine Suare Sezon
        Reji Plato Kulis Dekor Mizansen Sorti Piruet Viraj Rekolte Angajman Aranjman Abonman
        Anons Randevu Antre Vernisaj Finisaj Kadans Diyez Bemol Arpej Akort Sonat Sonet
        Kanto Füg Etüd Prelüd Koda Duet Kuartet Natürel
    """,
    "Latince kökenli -al / -el / -er (Radyal çizgisi)": """
        Radyal Aksiyal Lineer Fokal Lateral Frontal Sentral Nodal Modal Tonal Vokal Mural
        Manüel Vizüel Virtüel Aktüel Ritüel Sensüel Liminal Marjinal Primal Seminal Terminal
        Ordinal Kardinal Optimal Minimal Maksimal Spektral Boreal Austral Apikal Sagital Orbital
        Spiral Polar Radyan Radyus Oval Formel Total Real Natüral Vertikal Diyagonal Horizontal
        Ortogonal Eksantrik Konsantrik
    """,
    "Yunanca kökenli -ik (yapı, biçim, hareket)": """
        Tektonik Kinetik Statik Dinamik Arkaik Lirik Epik Poetik Kozmik Mitik Organik Grafik
        Optik Fotik Sferik Eliptik Prizmatik Kübik Konik Simetrik Sinoptik Hermetik Eklektik
        Sentetik Didaktik Kromatik Akromatik Fonetik Teknik Kritik Plastik Mistik Kaotik
    """,
    "Fransızca -aj / -ür / -et (zanaat ve işlem)": """
        Kolaj Dekupaj Montaj Kadraj Metraj Drapaj Brikolaj Asamblaj Frotaj Grataj Fumaj Mulaj
        Laminaj Dublaj Ajustaj Kalibraj Satinaj Faktür Tekstür Nervür Kontür Armatür Kupür
        Figür Natür Silüet Palet Rozet Plaket Lünet Sonet Piruet Briket Kaset Bonet Vinyet
    """,
    "Fransızca -ör (alet ve kişi)": """
        Vektör Kolektör Konservatör Restoratör Dekoratör Kompozitör Projektör Reflektör
        Konnektör Tensör Rezonatör Sektör Faktör Rotor
    """,
    "Işık ve görüntü (kısa teknik)": """
        Flu Spot Net Fokus Zum Halojen Neon Lazer Puls İmpuls Fluks Eko Faz Lümen Kelvin
        Lüks Diyafram Kontrjur Refle Prizma Spektrum
    """,
    "İtalyanca ödünç (müzik, denizcilik, Levanten)": """
        Vira Fora Alarga Iskota Randa Gondol Lagün Kampana Tombala Kumpanya Fiyaka Largo Lento
        Presto Forte Legato Rubato Fermata Kantat Tenor Alto Soprano Opera Arya
    """,
    "Bediz izinde: eski Türkçe ve yalın Türkçe (yeni)": """
        Görk Yalgın Esrik Yalaz Yultuz Tuman Kuyaş Kalık Ögdi Keçe Cicim Zili Mazı Zaç Rastık
        Kor Köz Kurum Bezek Körk Yaruk Bitig Ürüng Tolun Töz Uz Kut Tamga Otağ Bengü Kün Ög
    """,
}

# ---------------------------------------------------------------------------
# 2. Eleme kuralları (sırayla; ilk eşleşen gerekçe kaydedilir)
# ---------------------------------------------------------------------------
KISI_ADI = set("""
Tan Ufuk Bahar Meltem Poyraz Ayaz Defne Filiz Sedef Yeşim Bengü Tolun Yağız Derin Duru Nadir
Seher Şafak Hazan Mercan Firuze Lâl Erdem Pertev Lema Ziya Kamer Şule Hale Iris Vera Mira Kora
Sienna Marina Esin Serap Ekin Sima Pınar Atlas Alaca Kumsal Yaruk Opal Lila Damla Sevda
Gurup Zümrüt Akik Kehribar Mürdüm Nazar Ilgar Yultuz Tuman Kuyaş Kalık Lale Tenor
""".split())

# Aramalarda bulunan benzerlikler (03–07. turlar) ve yaygın bilinen büyük marka/kurum adları
CAKISMA = {
    "Pentimento": "İstanbul İstiklal'de 'Pentimento Art Shop' var (aramada bulundu)",
    "Mimesis": "Türkiye'de 'Mimesis' tiyatro dergisi var (aramada bulundu)",
    "Pictor": "New York'ta 'Pictor Gallery' kolektifi var (aramada bulundu)",
    "Ecce": "ABD Fargo'da 'ecce Art Gallery' var (aramada bulundu)",
    "Imago": "Benetton 'Imago Mundi' ve Lizbon 'Galeria Imago' (aramada bulundu)",
    "Imagora": "Lizbon 'Galeria Imago' ile çok yakın (aramada bulundu)",
    "Longa": "Fransa'da 'Galerie Ars Longa' var (aramada bulundu)",
    "Imprima": "Finlandiya'da 'Imprimo' baskı atölyesi/yayıncı var (aramada bulundu)",
    "Tamga": "Ayvalık'ta 'Tamgalar' sergisi; ad sanat çevresinde kullanılmış (aramada bulundu)",
    "Paragone": "Los Angeles'ta 'Paragone Gallery' kaydı; sergi adı olarak yaygın (aramada bulundu)",
    "Mimoza": "Helsinki 'Mimosa Galleria'; Türkiye'de ticari olarak çok yaygın",
    "Hece": "Türkiye'de 'Hece Yayınları' var",
    "Pasaj": "İstanbul'da 'Pasaj' adlı bağımsız sanat mekânı var",
    "Kare": "İstanbul'da 'Kare' adlı galeriler/sanat mekânları var",
    "Silsile": "Pakistan'da 'Silsila' sergi serisi; dinî çağrışım",
    "Disegno": "Londra'da 'Disegno' tasarım dergisi var",
    "Bottega": "Bottega Veneta markasıyla özdeş",
    "Pozitif": "İstanbul'da büyük konser organizatörü 'Pozitif' var",
    "Eksen": "İstanbul'da 'Radyo Eksen' var",
    "Ekol": "Türkiye'de büyük lojistik firması 'Ekol' var",
    "Petrol": "'Petrol Ofisi' ile özdeş",
    "Final": "Türkiye'de 'Final' eğitim kurumları var",
    "Tempo": "Türkiye'de 'Tempo' dergisi geçmişi var",
    "Platin": "Türkiye'de 'Platin' ekonomi dergisi var",
    "Atlas": "Türkiye'de 'Atlas' dergisi var; çok yaygın marka",
    "Titan": "Çok yaygın marka adı",
    "Cobra": "Bira ve otomobil markası olarak yaygın",
    "Zero": "Çok yaygın marka adı",
    "Neon": "Çok yaygın marka adı",
    "Kristal": "Türkiye'de çok sayıda 'Kristal' markası var",
    "Polar": "Spor saati ve kumaş markası olarak yaygın",
    "Kanon": "Sesi 'Canon' markasına çok yakın",
    "Nadir": "Gallery Artist kurucusu Nadir Erenler; sanat çevresinde karışır",
    "Sanatorium": "İstanbul'da 'Sanatorium' galerisi var",
    "Mana": "İstanbul'da 'Galeri Manâ' var",
    "Kanto": "Beyoğlu'nda çok sayıda 'Kanto' mekânı/etkinliği var",
    "Opera": "Opera binası ve tarayıcı markasıyla özdeş",
    "Plato": "Platon ve televizyon platosu çağrışımı; Türkiye'de çok sayıda 'Plato' işletmesi var",
    "Vitrin": "Türkiye'de çok sayıda 'Vitrin' işletmesi/dergisi var",
    "Spektrum": "Çok yaygın şirket adı",
    "Kuantum": "Çok yaygın şirket adı",
    "Prizma": "Türkiye'de çok yaygın yayınevi/şirket adı",
    "Avangart": "Çok yaygın şirket adı",
    "Antrepo": "Gümrük deposu olarak resmî bir terim; İstanbul Modern'in eski binası 'Antrepo 4'",
}

OLUMSUZ = {
    "Mumya": "Ölüm ve ceset çağrışımı",
    "Caput Mortuum": "Anlamı 'ölü kafa'",
    "Vanitas": "Ölümlülük ve boşunalık anlamı; bir galeri için karanlık",
    "Memento": "Memento mori, yani 'öleceğini hatırla' çağrışımı",
    "Pietà": "Dinî ikonografi",
    "Nabi": "Dinî anlam (peygamber)",
    "Tecelli": "Dinî ve tasavvufi anlam",
    "Hüzün": "Hüzün markası; satış mekânı için olumsuz",
    "Sus": "Emir kipi: 'sus!'",
    "Kesme": "Emir kipi: 'kesme!'; ayrıca kesmek",
    "Kalk": "Emir kipi: 'kalk!'",
    "Pes": "'Pes etmek' yani vazgeçmek deyimi",
    "Çal": "'Çalmak' fiilinin emri (hırsızlık çağrışımı)",
    "Pus": "İngilizcede 'pus' irin demek",
    "Lame": "İngilizcede 'lame' yani zavallı, kötü demek",
    "Flu": "İngilizcede 'flu' grip demek; uluslararası okunuşta olumsuz",
    "Zırnık": "'Zırnık koklatmam' yani hiçbir şey vermem deyimi",
    "Klişe": "Türkçede 'basmakalıp' anlamı baskın",
    "Kalıp": "Türkçede 'basmakalıp, stereotip' anlamı",
    "Paravan": "Türkçede 'paravan şirket' yani perde arkası anlamı",
    "Plastik": "Ucuzluk çağrışımı",
    "Odalisk": "Oryantalist çağrışım",
    "Akt": "Çıplak figür anlamı; kurumsal iletişimde hassas",
    "Kaşmir": "Siyasi bölge adı",
    "Cıva": "'Cıva gibi' yani yerinde duramayan deyimi; zehir",
    "Kurşun": "Mermi çağrışımı",
    "Kadmiyum": "Zehirli metal çağrışımı",
    "Kor": "Türkçede 'kör' ile karışabilir",
    "Negatif": "Olumsuz anlam",
    "Kuru": "Sıkıcı ve kuru anlamı baskın",
    "Yarım": "Eksik ve yarım kalmış anlamı",
    "Tortu": "Atık çağrışımı",
    "Balçık": "Çamur çağrışımı",
    "Banyo": "Gündelik banyo anlamı baskın",
    "Ham": "'Ham' yani olgunlaşmamış; İngilizcede jambon",
    "Talk": "İngilizcede 'konuşmak'; pudra çağrışımı",
    "Argon": "Türkçede 'argo' ile karışır",
    "Kripton": "Süpermen'in gezegeni çağrışımı baskın",
    "Marjinal": "Türkçede 'aykırı, uç' anlamı olumsuz okunabilir",
    "Sorti": "Askerî 'sorti' anlamı",
    "Fiyaka": "'Fiyaka yapmak' yani gösteriş deyimi",
    "Tombala": "Şans oyunu",
    "Pavyon": "Türkçede gece kulübü çağrışımı",
    "Kumpanya": "'Kumpanya' yani düzenbaz grup çağrışımı",
    "Dublaj": "Seslendirme anlamı baskın; özgünlükle çelişir",
    "Replik": "'Kopya' anlamı; özgün sanat için olumsuz",
    "Rötuş": "'Düzeltilmiş, makyajlanmış' çağrışımı",
    "Aktüel": "Türkçede magazin ve aktüel dergi çağrışımı",
    "Sensüel": "Cinsel çağrışım",
    "Terminal": "Otogar terminali ya da ölümcül hastalık çağrışımı",
    "Seminal": "Biyolojik anlamı baskın",
    "Primal": "İlkel ve hayvani çağrışım",
    "Kritik": "'Kritik durum' çağrışımı",
    "Kaotik": "Kaos anlamı",
    "Mistik": "Dinî ve mistik çağrışım",
    "Hermetik": "'Kapalı, erişilmez' anlamı",
    "Didaktik": "'Öğretici, sıkıcı' anlamı",
    "Sentetik": "'Yapay' anlamı",
    "Kurum": "Bürokratik ve resmî 'kurum' anlamı baskın",
    "Rastık": "Mezar taşı ve eski kozmetik çağrışımı; eskimiş",
    "Zaç": "Zehirli kimyasal (vitriyol)",
    "Kut": "Ses olarak 'kutu' ve İngilizce 'cut' ile karışır",
    "Us": "İngilizcede 'us' zamiri; aramada kaybolur",
    "Uz": "Çok kısa; 'uzun' kökü sanılır, aramada kaybolur",
    "Ög": "'ğ' harfi yabancı okuyucu için okunmaz",
    "Köz": "Mangal çağrışımı",
    "Rotor": "Mekanik parça çağrışımı",
    "Sektör": "İş dünyası jargonu",
    "Faktör": "İş dünyası jargonu",
    "Tensör": "Matematik jargonu",
    "Rezonatör": "Teknik jargon",
    "Konnektör": "Elektronik parça",
    "Kolektör": "Elektrik/egzoz parçası çağrışımı",
    "Konservatör": "'Tutucu' siyasi anlamı",
    "Lüks": "Gösteriş çağrışımı; ayırt edici değil",
    "Natürel": "Kozmetik ve gıda etiketlerinde yaygın",
    "Esans": "Parfüm ve gıda aroması çağrışımı",
    "Briket": "İnşaat bloğu çağrışımı",
    "Kaset": "Eskimiş müzik kaseti çağrışımı",
    "Bonet": "Bebek şapkası",
    "Mulaj": "Adli tıp ve maske çağrışımı",
    "Fumaj": "Tütsüleme çağrışımı",
    "Laminaj": "Endüstriyel işlem",
    "Ajustaj": "Endüstriyel işlem",
    "Kalibraj": "Endüstriyel işlem",
    "Satinaj": "Endüstriyel işlem",
    "Metraj": "İnşaat/kumaş ölçümü çağrışımı",
    "Brikolaj": "'Kendin yap' tamirat çağrışımı",
    "Angajman": "Askerî ve siyasi 'angajman kuralları' çağrışımı",
    "Abonman": "Abonelik anlamı",
    "Anons": "Hoparlör anonsu",
    "Gişe": "Bilet gişesi; ticari",
    "Vestiyer": "Gardırop ve vestiyer çağrışımı; gündelik eşya",
    "Lavabo": "Banyo lavabosu çağrışımı",
    "Gardırop": "Ev mobilyası çağrışımı",
    "Komodin": "Mobilya",
    "Tabure": "Mobilya",
    "Hangar": "Uçak hangarı",
    "Şantiye": "İnşaat alanı",
    "Abajur": "Ev eşyası",
    "Avize": "Ev eşyası",
    "Parke": "Zemin kaplaması",
    "Karo": "Fayans ve iskambil çağrışımı",
    "Kurdele": "Hediye paketi çağrışımı",
    "Bandrol": "Vergi bandrolü çağrışımı",
    "Apre": "Kumaş kimyasalı",
    "Trikotaj": "Tekstil sanayi çağrışımı",
    "Makrome": "Hobi el işi çağrışımı",
    "Dosya": "Büro çağrışımı",
    "Envanter": "Muhasebe çağrışımı",
    "Broşür": "Reklam çağrışımı",
    "Bülten": "Haber bülteni",
    "Vize": "Pasaport vizesi",
    "Viza": "Bürokratik onay",
    "Etiket": "Fiyat etiketi çağrışımı",
    "Amblem": "Logo anlamı",
    "Arma": "Hanedan arması",
    "Kalibre": "Silah kalibresi çağrışımı",
    "Gabari": "Teknik ölçü (yük gabarisi)",
    "Şablon": "'Kalıp, taklit' anlamı",
    "Fiksatif": "Sprey malzeme; kuaför çağrışımı",
    "Etalaj": "Ticari mal teşhiri anlamı",
    "Randevu": "Gündelik ve klinik çağrışım",
    "Rande": "Kısaltma; argo",
    "Turne": "Tiyatro turnesi",
    "Matine": "Sinema seansı",
    "Rekolte": "Tarım ürünü çağrışımı baskın",
    "Gondol": "Market rafı ve Venedik çağrışımı",
    "Lagün": "Tatil köyü çağrışımı",
    "Kampana": "Fren kampanası",
    "Iskota": "Denizcilik jargonu; 'ı' ile başlıyor",
    "Randa": "Denizcilik jargonu",
    "Alarga": "Denizcilik jargonu",
    "Fora": "'Fora etmek' yani açmak, çıkarmak; argo",
    "Vira": "'Vira' yani durmadan; ayrıca demir alma komutu",
    "Halojen": "Ampul tipi",
    "Lazer": "Lazer tedavi ve epilasyon çağrışımı",
    "Zum": "Çevrimiçi toplantı yazılımı çağrışımı",
    "Net": "İnternet ve 'net kâr' çağrışımı",
    "Eko": "Ekonomi ve ekoloji kısaltması",
    "Puls": "Tıbbi nabız",
    "İmpuls": "Fizik jargonu",
    "Fluks": "Fizik jargonu",
    "Arya": "Kişi adı ve ideolojik çağrışım",
}

JENERIK = set("""
Galeri Atelier Atölye Vernisaj Finisaj Sanat Resim Tablo Desen Kolaj Gravür Litografi Serigrafi
Afiş Portre Otoportre Eskiz Etüt Etüd Kroki Maket Edisyon Albüm Portfolyo Palet Şövale Tuval Kanvas
Figür Figura Pictura Opus Akademia Accademia Museion Pinakotek Butik Salon Tasvir Nakkaş
Kalemişi Levha Kıta Monokrom Polikrom Kromatik Akromatik Pastel Pastoral Allegori Arabesk Grotesk
Marina Katalog Arşiv Repertuvar Koleksiyon Dekor Mizansen Kulis Sezon Prova Konser Sonat Sonet
Kantat Opera Tenor Alto Soprano Grafik Teknik Optik Fotik Simetrik Organik Mural Muralizm
Minimal Maksimal Optimal Kinetik Statik Dinamik Lirik Epik Poetik Kozmik Mitik Arkaik Eklektik
Kübik Konik Sferik Eliptik Prizmatik Sinoptik Fonetik Total Real Natüral Formel Oval Spiral
Ritüel Manüel Vizüel Virtüel Vokal Kardinal Ordinal Liminal Natür Montaj Kadraj Kontür Kupür
Silüet Siluet Asamblaj Dekupaj Frotaj Grataj Drapaj Rölöve Medalyon Rozet Plaket Lünet Vinyet
Bordür Kartuş Paspartu Filigran Gramaj Kuşe Ozalit Kalk Tiraj Fasikül Faktür Tekstür Nervür
Figür Armatür Restoratör Dekoratör Kompozitör Projektör Reflektör Vektör Fokus Kelvin Lümen
Diyafram Kontrjur Refle Prizma Spektrum Spot Faz Piruet Duet Kuartet Arpej Akort Diyez Bemol
Kadans Füg Prelüd Koda Legato Rubato Fermata Lento Presto Forte Largo Debü Antrakt Avan
Prömiyer Repriz Bis Jest Suare Reji Sorti Viraj Aranjman Kaşe Paraf Monogram Estamp Guaj Biblo
""".split())
# Not: JENERIK listesi yalnızca ÖNCEKİ kurallardan sağ çıkan ve aşağıdaki
# "ayırt_edici_degil" kuralında kullanılan, gündelik ya da betimleyici kelimeleri tutar.
# Antre çizgisinin güçlü adayları (Debü, Antrakt, Avan, Kaşe, Paraf, Estamp, Guaj, Faktür, Tiraj...)
# burada YER ALMAZ; aşağıda KORU kümesiyle ayrılır.

KORU = set("""
Antre Radyal Bej Opak Meridyen Bediz Debü Antrakt Avan Kaşe Paraf Estamp Guaj Faktür Tiraj
Antresol Etaj Mezanin Parter Atik Fuaye Ajur Velur Vual Muare Gobelen Düble Masif Maroken Glase
Aksiyal Lineer Fokal Sagital Boreal Austral Apikal Nodal Modal Tonal Spektral Vertikal Lateral
Frontal Sentral Orbital Eksantrik Konsantrik Ortogonal Diyagonal Radyan Radyus Tektonik Kinetik
Fasikül Filigran Paspartu Vinyet Kartuş Lünet Plaket Biblo Kadans Diyez Bemol Fermata Largo
Repriz Prömiyer Reji Viraj Ekru Füme Nötr Degrade Nüans Satine Metalik Brüt Plise Drape Gofre
Kontrjur Refle Fokus Spot Faz Kelvin Lümen Diyafram Silüet Kontür Rölyef Rakurs Friz Rozet
Gnomon Zenit Azimut Albedo Grafit Kolofon Verso Seladon Mürdüm Sedef Antrasit Kobalt Siyan
Krom İridyum Rodyum Vanadyum Selenyum Bizmut Fraktal Matris Modül Görk Yalgın Esrik Yalaz
Keçe Cicim Mazı Bezek Körk Ürüng Töz Kün Otağ Tolun Paralel Ekvator Orbit Apsis Teğet Usturlap
Lüster Emaye Patina Gren Hale Kadraj Montaj Kolaj Asamblaj Kupür Mulaj Sonet Piruet Duet Arpej
Akort Koda Prelüd Jest Bis Suare Mizansen Kulis Fuaye Arkad Portik Rotonda Belveder Peron Niş
Kabin Korniş Panjur Aplik Brokar Fular Volan Organze Gipür Brode Krep Şifon Tül Kalk Gramaj
Kuşe Ozalit Klişe Rötuş Rölöve Estamp Gravür Edisyon Etap Esplanad Vestibül Podyum Kordon
Atriyum Portal Lobi Veranda Suit Budoar Şale Şato
""".split())

FOREIGN_RE = re.compile(r"[qwxāēīōūéèêàòóíúàäëïÿñ]|sch|gh|th|ph|zz|cc|tt|ss|ll|gn|ou|ae|œ", re.I)
VOWELS = set("aeıioöuüâîûAEIİOÖUÜÂÎÛ")


def hece(word):
    return sum(1 for ch in word if ch in VOWELS)


def topla():
    havuz = OrderedDict()
    for f in sorted(glob.glob(str(ROOT / "docs/galeri/0[4-9]*.md")) + glob.glob(str(ROOT / "docs/galeri/10*.md"))):
        aile = Path(f).stem
        for line in open(f, encoding="utf-8"):
            if not (line.startswith("|") or line.startswith("- ")):
                continue
            m = re.search(r"\*\*([^*]{1,40})\*\*", line)
            if not m:
                continue
            for part in re.split(r"\s*/\s*", m.group(1).strip()):
                if part and not any(c.isdigit() for c in part):
                    havuz.setdefault(part, {"aile": aile, "kaynak": "önceki turlar"})
    for aile, blok in YENI.items():
        for w in blok.split():
            havuz.setdefault(w, {"aile": aile, "kaynak": "gece turu"})
    return havuz


def gerekce(ad):
    """İlk eşleşen eleme gerekçesini döndürür; ad sağ kalırsa None."""
    if ad in BEGENILEN:
        return None
    if "&" in ad or " " in ad or "-" in ad:
        return "1. Birden çok kelime: istenen tarz sade, tek kelime"
    if ad in CAKISMA:
        return "2. Bilinen benzerlik/çakışma: " + CAKISMA[ad]
    if ad in KISI_ADI:
        return "3. Türkiye'de yaygın kişi adı: marka olarak ayırt edici değil, aramada kaybolur"
    if ad in OLUMSUZ:
        return "4. Olumsuz, uygunsuz ya da yanlış yönlendiren çağrışım: " + OLUMSUZ[ad]
    if ad in KORU:
        return None
    if FOREIGN_RE.search(ad):
        return "5. Türkçe yazımı yok: Antre/Radyal çizgisi Türkçeleşmiş kelimeler; okunuşu ve yazımı zor"
    h = hece(ad)
    if h > 3 or len(ad) > 9:
        return f"6. Uzun ({h} hece, {len(ad)} harf): Antre ve Radyal 2 hece, en fazla 3 hece hedefleniyor"
    if ad.endswith("izm") or ad.endswith("ism"):
        return "7. Bir sanat akımının adı: galeri tek bir akımla özdeşleşir"
    if ad not in KORU and ad in JENERIK:
        return "8. Betimleyici/jenerik sanat kelimesi: marka tescili ve ayırt edicilik zayıf"
    return None


GUNDELIK = set("""
Kat Doku Çizgi Kalem Kapı Hol Teras Depo Han Plan Oran Gram An Ölçü Pamuk Lif İplik Örgü Kilim
Desen Kum Krem Kül Mat Poz Kare Nota Ritim Tempo Solo Duo Nokta Virgül Harf Satır Paragraf Sis
Tohum Yosun Zeytin Yalın Sade Saf Öz Taze Bütün Ara İç Dış Ön Arka Yan Ton Fon Kontrast Odak
Açı Rota Eşik Kemer Kubbe Kolon Cephe Konsol Gri Bordo Lila Pudra Hardal Haki Kadife Saten
Dantel Jarse Flaş Pozitif Kontak Makara Basma Ilık Durgun Dingin Kil Alçı Kireç Mermer Granit
Lens Ekran Format Seri Kum Taş Krem Kuvars Mika Çakıl Çakmak Damar Kristal Reçine Polen Liken
Fide Tohum Kırağı Çiy İmbat Lodos Alaca Gurup İkindi Sis Dipnot Satır İmla Ayraç Parantez Tire
Kısa Asteriks Ampersan İnisyal Akor Fasıl Taksim Makam Usul Perde Mızrap Peşrev Tını Es Tiz
Oktav Prelüd Enstantane Netlik Obtüratör Vizör Fiks Bezir Kasnak Kanvas Jüt Atkı Çözgü Muslin
Tafta Poplin Gabardin Şile Patiska Çuha Terrakota Traverten Bazalt Tüf Oniks Kalsit Obsidyen
Yeşim Ekinoks Solstis Ufuk Rakım İrtifa Mihver Kerte Pusula Kadran Rasat Kesit Ölçek Enlem
Boylam Avlu Cumba Nis Tonoz Kiriş Mahzen Ambar Arasta Bedesten Folyo Tabaka Punto Serif Font
Dizgi Marj Grid Mizanpaj Künye Hamiş Ekslibris Ofset Tipo Riso Bristol Endaze Arşın Karış
Kulaç Dirhem Miskal Okka Kantar Fersah Menzil Karat Mikron Milim Kıvam Vezin Lahza Hokka Divit
Kamış Mıstar Pergâr Sakız Damar Kopal Şellak Kazein Tutkal Terebentin Telaro Papirüs Kenevir
Mastik Sandarak Lâcivert Lapis Azur Okr Çivit Murex Smalt Bistre Is Fildişi Samur Cehri
Turkuaz Azurit Malakit Realgar Seruleum Viridian Lake Napoli Prusya Varak Bolus Patina Karton
Linol Burin Monotip Kamayö Ebru Kore Putto Karyatid Arkadya Emblema Effigies Manken Kroma
Doygunluk Kolorit Simultane Şavk Kökboya Zağferan Pinax Kırmız Zincifre Sinopia Velatura Lavi
Tarama Plein Trompe Sanguine Gesso Keten Vernis Sepya Vellum Tabula Umbra Kontrapost Valör
Tondo Torso Büst Profil Gestus Phi Triptik Diptik Pandan Lünet Veduta Zemin Nüans Kalon Pathos
Katharsis Punctum Ekphrasis Lonca Gedik Revak Murakka Halkâr Şemse Âhar Tahrir Sûret Hâre Mühre
Çintemani Zeuxis Linea Fauve Brücke Secession Gutai Povera Informel Purizm Novecento Kouros
Pensée Bozzetto Modello Abbozzo Ricordo Spolvero Giornata Intonaco Arriccio Unione Tempera Fresko
""".split())

# Osmanlıca ve klasik ağırlıklı; modern-sade çizgiye uzak
OSMANLI = set("""
Zerefşan Halkâr Âhar Mühre Murakka Tahrir Şemse Hiref Hünerver Tenasüp Revnak Hurde Nüsha Nadide
Zerre Rakam Nakş Mizan Tarh Ahenk Tezat Endaze Arşın Dirhem Miskal Okka Fersah Kantar Vezin Lahza
İrtifa Mihver Kündekâri Malakâri Telkâri Savat Salbek Köşebent Zencerek Penç Rumi Hatayi Mıklep
Sertab Hokka Divit Mıstar Pergâr Zağferan Seyr Hayret Zevk Gedik Lonca Revak Bedesten Arasta
Mahzen Menzil Yaraşık Ulam Dem Fer Şavk Hâre Sûret Tasvir Çintemani Cehri Zincifre Kırmız Lâcivert
Mürdüm Peşrev Mızrap Usul Makam Fasıl Rasat Usturlap Tombak Lüster Sıraltı Edirnekâri Varak
""".split())


def ikinci_tur(ad, bilgi):
    """Birinci turdan sağ çıkanlar için marka gücü elemesi."""
    if ad in BEGENILEN or ad in KORU:
        return None
    if ad in OSMANLI:
        return "9. Osmanlıca/klasik ağırlık: istenen modern ve sade çizgiye uzak"
    if ad in GUNDELIK:
        return "10. Çok gündelik ya da dar teknik kelime: marka olarak ayırt edici değil, aramada kaybolur"
    return "11. Antre/Radyal çizgisine uzak: Türkçeleşmiş, iki-üç heceli, mekân/yön/yüzey anlamı taşıyan çekirdek kümeye girmedi"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    havuz = topla()
    satirlar, sayac = [], Counter()
    for ad, bilgi in havuz.items():
        g = gerekce(ad) or ikinci_tur(ad, bilgi)
        durum = "elendi" if g else "kısa liste"
        sayac[(g or "SAĞ KALDI").split(":")[0]] += 1
        satirlar.append({"isim": ad, "aile": bilgi["aile"], "kaynak": bilgi["kaynak"],
                         "hece": hece(ad), "durum": durum, "gerekce": g or ""})
    with open(OUT / "havuz.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(satirlar[0].keys()))
        w.writeheader()
        w.writerows(satirlar)
    with open(OUT / "eleme-ozeti.txt", "w", encoding="utf-8") as fh:
        fh.write(f"Toplam aday: {len(havuz)}\n")
        for k, v in sorted(sayac.items()):
            fh.write(f"{v:5d}  {k}\n")
    print(open(OUT / "eleme-ozeti.txt", encoding="utf-8").read())
    kisa = [s["isim"] for s in satirlar if s["durum"] == "kısa liste"]
    print(len(kisa), ", ".join(kisa))




# ---------------------------------------------------------------------------
# 3. Üçüncü tur: ilk iki turdan sağ çıkan 194 isim tek tek değerlendirildi
# ---------------------------------------------------------------------------
TUR3 = {
    "Kobalt": "Renk ve kimya kelimesi olarak yaygın; ayırt edici değil",
    "Kadraj": "Fotoğraf ve sinema dünyasında çok kullanılan bir terim; ayırt edici değil",
    "Nüans": "Çok gündelik; sıfat gibi kullanılıyor, pek çok işletme adı",
    "Patina": "Mobilya ve dekorasyon sektöründe çok yaygın",
    "Gravür": "Bir baskı tekniğinin adı; betimleyici",
    "Kolaj": "Bir tekniğin adı; betimleyici",
    "Edisyon": "Yayın terimi; betimleyici",
    "Lüster": "Avize ve çini parlaklığıyla karışır",
    "Körk": "Okunuşu 'kürk' ile karışır",
    "Töz": "'Öz' ile karışır, anlamı belirsiz kalır",
    "Ekru": "Türkiye'de sesi neredeyse aynı olan 60 mağazalı 'Ecrou' perakende zinciri var (gece taramasında bulundu)",
    "Füme": "'Füme balık, füme et' çağrışımı baskın",
    "Antrasit": "Kömür ve inşaat boyası çağrışımı; sert ses",
    "Grafit": "Sanayi ve kırtasiye ürünlerinde çok yaygın",
    "Siyan": "'Siyanür' çağrışımı",
    "Emaye": "Tencere ve mutfak eşyası çağrışımı",
    "Gren": "Çok teknik; okunuşu belirsiz",
    "Refle": "Kuaför 'röfle'siyle karışır",
    "Kelvin": "Fizik birimi ve aydınlatma markası",
    "Lümen": "Fizik birimi; 'Lumen' çok yaygın marka",
    "Diyafram": "Tıbbi (diyafram kası) çağrışımı",
    "Paralel": "Türkiye'de 'paralel yapı' siyasi çağrışımı",
    "Ekvator": "Coğrafya terimi; galeriyle bağı zayıf",
    "Azimut": "Azimut yat markası ile özdeş",
    "Usturlap": "Uzun ve tarihî; müze objesi çağrışımı",
    "Orbit": "Orbit sakız markası",
    "Apsis": "Tıbbi 'apse' ile karışır",
    "Teğet": "'Teğet geçmek', yani kıl payı ıskalamak deyimi",
    "Bezek": "'Bez' ve bebek bezi çağrışımı",
    "Otağ": "Restoran ve düğün salonu adı olarak yaygın",
    "Kün": "Anlaşılmaz; 'kin' ile karışır",
    "Ürüng": "Okunuşu zor ('ü' ve 'ng')",
    "Rölöve": "Mimari ölçüm jargonu; iki 'ö' ile okunuşu zor",
    "Ozalit": "Fotokopi ve ozalit dükkânı çağrışımı",
    "Gramaj": "Kâğıt ağırlığı; ticari ve teknik",
    "Kuşe": "Bir kâğıt türü; matbaa jargonu",
    "Tül": "Tül perde çağrışımı",
    "Brüt": "'Brüt maaş' çağrışımı",
    "Fokus": "'Focus' ile aynı; dergi ve marka adı olarak yaygın",
    "Akort": "Çalgı ayarı; teknik",
    "Koda": "Anlamı 'kapanış'; yeni açılan bir galeriye ters düşüyor; 'kod' ile karışır",
    "Prelüd": "Honda Prelude otomobili; 'ü' harfi",
    "Degrade": "Kuaför ve tasarım jargonu; çok yaygın",
    "Satine": "'Satine boya' ürün adı",
    "Metalik": "Otomobil boyası çağrışımı",
    "Plise": "Moda ve etek çağrışımı",
    "Drape": "İngilizcede 'drape' perde demek; moda çağrışımı",
    "Gofre": "'Gofret' ile karışır",
    "Silüet": "Güzellik merkezi adı olarak çok yaygın",
    "Kontür": "Makyaj 'kontürü' çağrışımı",
    "Rölyef": "Heykel terimi; okunuşu zor",
    "Rozet": "Küçük, değersiz bir obje çağrışımı",
    "Kartuş": "Yazıcı kartuşu çağrışımı",
    "Friz": "Saçta 'frizli' çağrışımı; anlamı bilinmiyor",
    "Kulis": "'Kulis bilgisi', yani dedikodu ve perde arkası",
    "Mizansen": "Siyasette 'sahte gösteri' anlamında kullanılıyor",
    "Estamp": "Madrid'de 'Estampa' sanat fuarı ve 'Galería Estampa' var (gece taramasında bulundu)",
    "Krom": "Krom kaplama ve Google Chrome",
    "İridyum": "Iridium uydu telefonu markası; uzun",
    "Rodyum": "Kuyumcu kaplaması çağrışımı",
    "Vanadyum": "Uzun; kimya",
    "Selenyum": "Vitamin takviyesi çağrışımı",
    "Bizmut": "Mide ilacı çağrışımı",
    "Fraktal": "Matematik ve dijital/NFT çağrışımı",
    "Faz": "Elektrik fazı; çok kısa ve teknik",
    "Yalgın": "Anlamı neredeyse bilinmiyor; 'yalnız' ve 'yalan' ile karışır",
    "Esrik": "'Sarhoş' çağrışımı",
    "Yalaz": "Bilinmiyor; 'yalan' ile karışır",
    "Matris": "Matrix filmi; matematik",
    "Modül": "Mobilya ve yazılım jargonu",
    "Orbital": "Uzay jargonu",
    "Vestibül": "Tıbbi (kulak vestibülü) çağrışımı",
    "Lobi": "'Lobi faaliyeti' siyasi çağrışımı",
    "Arkad": "'Arcade' oyun salonu çağrışımı",
    "Portik": "Az bilinir; okunuşu belirsiz",
    "Portal": "İnternet portalı çağrışımı",
    "Atriyum": "Kalp anatomisi ve AVM atriyumu",
    "Rotonda": "Türkiye'de az bilinir; trafik göbeği çağrışımı",
    "Belveder": "Viyana'daki Belvedere müzesi ile özdeş",
    "Veranda": "Ev ve restoran çağrışımı",
    "Kordon": "İzmir Kordon'da çok sayıda işletme bu adı kullanıyor",
    "Peron": "Tren istasyonu ve Arjantinli Perón çağrışımı",
    "Podyum": "Moda podyumu",
    "Niş": "İş dünyasında 'niş pazar' jargonu; çok kısa",
    "Kabin": "Uçak ve soyunma kabini",
    "Esplanad": "Uzun ve bilinmiyor",
    "Vertikal": "Lineer ve Aksiyal aynı fikri daha kısa ve temiz anlatıyor",
    "Eksantrik": "Türkçede 'tuhaf, garip' anlamı baskın",
    "Konsantrik": "Uzun; matematik",
    "Diyagonal": "Uzun; geometri",
    "Lateral": "Tıp ve anatomi jargonu",
    "Frontal": "'Frontal' çıplaklık ve saldırı çağrışımı",
    "Sentral": "Jenerik 'merkezî'; çok sayıda işletme",
    "Ortogonal": "Uzun; matematik",
    "Radyus": "Kol kemiği (radius) çağrışımı",
    "Austral": "Arjantin'in eski para birimi; uzak",
    "Apikal": "Diş hekimliği jargonu",
    "Nodal": "Ağ ve tıp jargonu",
    "Modal": "Modal kumaş ve dilbilgisi; ticari",
    "Spektral": "'Hayaletimsi' anlamı",
    "Kinetik": "Kinetik sanat akımıyla özdeş; jenerik",
    "Spot": "'Spot ürün', yani indirim ve ikinci el çağrışımı",
    "Krep": "Krep (yiyecek) çağrışımı",
    "Şifon": "Şifonyer ile karışır; moda",
    "Organze": "Düğün ve moda çağrışımı",
    "Gipür": "Gelinlik çağrışımı",
    "Fular": "Moda aksesuarı",
    "Brode": "Tekstil işleme; ticari",
    "Aplik": "Duvar lambası çağrışımı",
    "Prömiyer": "Sinema galası; 'ö' harfi",
    "Bis": "Çok kısa; 'bisküvi'yi çağrıştırır",
    "Jest": "İngilizcede 'jest' şaka demek; 'jest yapmak' zoraki kibarlık",
    "Suare": "Elitist davet çağrışımı",
    "Etap": "Konut projelerinin 'etap'ları; inşaat çağrışımı",
    "Şale": "Dağ evi ve otel çağrışımı",
    "Şato": "Otel ve şarap çağrışımı",
    "Suit": "Otel süiti",
    "Budoar": "Yatak odası çağrışımı",
    "Korniş": "Perde rayı",
    "Panjur": "Pencere kepengi; ev eşyası",
    "Masif": "'Masif mobilya' çağrışımı",
    "Maroken": "Deri ve çanta; Fas çağrışımı",
    "Brokar": "Kumaş; uzak bir kelime",
    "Gobelen": "Goblen işi (hobi) çağrışımı",
    "Volan": "Otomobil volanı ve etek volanı",
    "Fasikül": "Tıp (kas fasikülü) çağrışımı; uzun",
    "Plaket": "Ödül plaketi çağrışımı",
    "Biblo": "Süs eşyası ve kitsch çağrışımı",
    "Reji": "Osmanlı tütün tekeli 'Reji' çağrışımı; anlamı bilinmiyor",
    "Piruet": "'Piruet atmak', yani kıvırmak deyimi",
    "Viraj": "Trafik çağrışımı baskın",
    "Diyez": "Türkçede '#' işaretinin, yani hashtag'in adı",
    "Bemol": "'Yarım ses düşük' anlamı",
    "Arpej": "Anlaşılmaz; müzik jargonu",
    "Sonet": "Şiir formu; edebiyat çağrışımı",
    "Duet": "Çok yaygın işletme adı",
    "Tektonik": "Türkiye'de deprem çağrışımı",
    "Montaj": "'Montaj', yani sahte fotoğraf ve iftira çağrışımı",
    "Asamblaj": "Uzun; teknik",
    "Kupür": "Gazete kupürü; 'kesik parça'",
    "Largo": "Türkiye'de bilinmiyor; İtalyanca 'yavaş'",
    "Keçe": "Hobi keçesi ve 'keçeli kalem' çağrışımı",
    "Cicim": "Çocuksu ve sevimli bir ses; ciddiyet zayıf",
    "Mazı": "'Mazi' (geçmiş) ile karışır",
}

# İlk 50: (isim, puan/25, neden seçildi, dikkat)
ILK50 = [
    ("Paraf", 24, "İmzanın baş harflerle atılan kısa hâli: sanatçının işareti. İki heceli, Fransızca kökenli ama Türkçede yaşayan bir kelime; Antre ile aynı tını. Galerinin 'onayladığı' sanatçı fikrini taşıyor", "Gece taramasında Türkiye'de ve Paris'te galeri ya da marka çıkmadı"),
    ("Antresol", 24, "'Katlar arası': zemin ile birinci kat arasındaki ara kat. Aynı binada iki ayrı markanın (müzayede ve galeri) olacağı yapıya birebir uyuyor. Antre'nin kardeşi", "Gece taramasında galeri çıkmadı; Fransızca 'entresol' yalnızca mimari terim olarak geçiyor"),
    ("Guaj", 23, "Guaş: opak suluboya. Opak'ın akrabası, tek hece, yabancıların da okuyabileceği bir ses (gwaş). Figür ve desen geleneğinin malzemesi", "Gece taramasında galeri ya da marka çıkmadı"),
    ("Etaj", 23, "Fransızca 'étage', yani kat. Kısa, karakterli 'j' harfi (Bej gibi). Galerinin binadaki yerini sade bir kelimeyle söylüyor", "Berlin'de 'GalerieETAGE', Paris'te kapanmış '5ème Etage' var; yazım farklı, risk hafif"),
    ("Antre", 22, "Sizin seçiminiz. 'Giriş': galerisi olmayan yetenekler için giriş kapısı", "İstanbul'da 'Antrepo' adlı bir sanat mekânı var; ses yakınlığı riski"),
    ("Radyal", 22, "Sizin seçiminiz. 'Merkezden dışa yayılan': bir merkezden sanatın yayılması", "Türkiye'de 'radyal lastik' ifadesi çok yaygın; otomotiv çağrışımı riski"),
    ("Bediz", 22, "Sizin beğendiğiniz. Göktürkçede 'resim, süs'; Türk resim dilinin bilinen en eski kelimesi", "Türkiye'nin ilk profesyonel fotoğrafçısı Bahaettin Rahmi Bediz'in soyadı; Karaköy'de 'Bediz Clothing' adlı bir tekstil firması kaydı var"),
    ("Vual", 23, "Fransızca 'voile', yani peçe: resmin üstüne çekilen ince, saydam katman. Tek hece, yumuşak ve modern", "Paris'te fotoğraf galerisi 'Galerie VU'' var; ses benzerliği zayıf"),
    ("Ajur", 23, "Işığın içinden geçtiği delikli işleme. Işık ile doku tek kelimede; iki hece, 'j' harfi", "Gece taramasında galeri ya da marka çıkmadı"),
    ("Fokal", 22, "'Odaksal': bakışın toplandığı nokta. Radyal ile aynı ailede, iki heceli", "Varşova'daki ünlü 'Foksal Gallery' ile tek harf fark; sanat dünyasında karışma riski"),
    ("Debü", 22, "İlk çıkış, ilk sergi. Genç sanatçılara ilk kapıyı açan bir galeri için birebir", "'ü' harfi yabancılar için zor; uluslararası yazımda 'Debu' olur"),
    ("Opak", 22, "Sizin öneriniz. Işığı geçirmeyen, yoğun yüzey; Guaj'ın da niteliği", "Sert ve sade; ön taramada sorun bilinmiyor"),
    ("Kolofon", 22, "Eski kitapların son sayfasındaki basım notu. Yunanca anlamı 'son dokunuş'; yayıncı galeri için güçlü", "Üç hece; kitap dünyası dışında az bilinir"),
    ("Filigran", 22, "Kâğıdın içine gömülü, ışığa tutunca görünen damga: görünmez kalite işareti", "Üç hece; kuyum sektöründe 'telkâri' anlamında da kullanılır"),
    ("Muare", 22, "Kumaşta ve baskıda dalga dalga parıltı (moiré). Yumuşak ve özgün bir ses", "'ua' ses dizisi yabancı okuyucu için belirsiz"),
    ("Glase", 22, "Sırlı ve parlak (glacé); resimde 'glaze', yani şeffaf sır katmanı", "'Glase kestane' ve 'glase deri' çağrışımı"),
    ("Rakurs", 22, "Perspektifte figürü kısaltarak çizmek: figüratif resmin en zor tekniği", "Sert bir ses; sanat dışında bilinmiyor"),
    ("Tiraj", 22, "Bir yayının baskı adedi. Yayıncı galeri ve edisyon fikri", "Gazete satış rakamlarını çağrıştırır"),
    ("Vinyet", 22, "Kenarları silikleşen küçük resim: dikkati merkeze çeken çerçeve", "'Vinyet' sigara paketlerindeki etiket anlamıyla da kullanılır"),
    ("Parter", 22, "Zemin kat ve Fransız bahçesi: binanın sokağa açılan katı", "Tiyatroda 'parter' salonu; spor 'partner' ile karışabilir"),
    ("Fuaye", 22, "Tiyatronun giriş salonu: buluşma, sohbet ve ilk izlenim yeri", "Tiyatro çağrışımı güçlü"),
    ("Repriz", 22, "Yeniden sahneleme: ustaların yeniden keşfi fikri", "'Repriz' sinema ve televizyonda tekrar yayın anlamında"),
    ("Kadans", 22, "Ritim, ölçü ve kapanış cümlesi: düzenli bir sergi programının metaforu", "Müzik dışında az bilinir"),
    ("Fermata", 21, "Müzikte notayı uzatma işareti (𝄐): zamanın durduğu an. Logosu hazır", "İtalyanca; üç hece"),
    ("Radyan", 21, "Açı birimi; sesi 'radiant', yani ışıldayan. Radyal'in kardeşi", "Radyal ile aynı ses ailesi; matematik çağrışımı"),
    ("Aksiyal", 21, "Eksen boyunca: bir çizgiye bağlılık, programın ekseni", "Üç hece; teknik"),
    ("Verso", 21, "Bir resmin arka yüzü: provenans etiketleri ve tarihin saklandığı yer", "Çok sayıda yabancı markada kullanılıyor"),
    ("Avan", 21, "'Önce, ön'; mimarlıkta 'avan proje', yani ilk tasarım", "'Avangart' kısaltması gibi okunabilir"),
    ("Kaşe", 21, "Üç anlamı var: mühür, sanatçıya ödenen ücret ve 'kaşesi var' deyimindeki prestij", "'ş' harfi; ilaç kaşesi çağrışımı"),
    ("Faktür", 21, "Resimde boyanın yüzeyde işlenişi; ressamın el izi", "Muhasebede 'fatura' anlamıyla karışabilir"),
    ("Gnomon", 21, "Güneş saatinin gölge düşüren çubuğu: gölgeyle zaman yazan alet. Resmin gölgeden doğduğu efsaneyle bağı var", "'Gn' ile başlıyor; Türkçede okunuşu yabancı"),
    ("Albedo", 21, "Bir yüzeyin ışığı yansıtma oranı: bilimsel ve sade", "İngiltere'de 'Albedo Marz' adlı bir sanatçı var"),
    ("Zenit", 21, "Göğün tepe noktası, doruk", "Zenit fotoğraf makinesi ve Zenit futbol kulübü"),
    ("Mezanin", 21, "Asma kat; Antresol'un İtalyanca kökenli eşi", "Mimari jargon; restoranlarda da kullanılır"),
    ("Atik", 21, "Çatı katı, ayrıca Türkçede 'çevik, tetik': çift anlam", "'Atik' bazı soyadlarında var"),
    ("Düble", 21, "'Çift' ve altın kaplama: aynı binada iki marka fikri", "'Düble rakı' çağrışımı"),
    ("Velur", 21, "Kadife: yumuşak bir ses ve dokunsal bir anlam", "Tekstil sektöründe ürün adı"),
    ("Görk", 21, "Eski Türkçede 'güzellik', görkem kelimesinin kökü. Bediz ailesinden, tek hece", "'ö' harfi; anlamı açıklama ister"),
    ("Lineer", 20, "Çizgisel: desen ve çizgi geleneği", "Matematik ve 'lineer cebir' çağrışımı"),
    ("Sagital", 20, "Bedeni ikiye bölen düzlem; kökü Latince 'ok'", "Anatomi jargonu"),
    ("Boreal", 20, "Kuzeye ait; 'aurora borealis', yani kuzey ışıkları", "Bazı yabancı markalarda kullanılıyor"),
    ("Antrakt", 20, "İki perde arasındaki an; Antre'nin akrabası", "'kt' ile bitiş sert"),
    ("Paspartu", 20, "Resmin çevresindeki karton; kelimenin anlamı 'her kapıyı açan'", "Üç hece; çerçeveci dükkânlarında kullanılır"),
    ("Kontrjur", 20, "Işığa karşı çekim: figürü arkadan gelen ışıkla göstermek", "Okunuşu zor"),
    ("Lünet", 20, "Kemer altındaki yarım daire resim", "'ü' harfi"),
    ("Seladon", 20, "Topkapı'nın koleksiyonuyla ünlü yeşimsi seramik yeşili", "Üç hece; renk adı olarak az bilinir"),
    ("Nötr", 19, "Tarafsız renk; müzayededen bağımsız bir galerinin sessiz metaforu", "'ö' harfi ve ünsüz kümesi"),
    ("Tonal", 19, "Tona ait: renk ve ışık ilişkisi", "Sıfat; tek başına zayıf"),
    ("Meridyen", 19, "Sizin öneriniz. Boylam çizgisi, yani yeryüzünü bölen ince çizgi", "Le Méridien otel zinciri ile güçlü çağrışım; Türkiye'de çok sayıda 'Meridyen' işletmesi"),
    ("Bej", 18, "Sizin öneriniz. En sade renk adı", "Çok yaygın bir renk adı; kafe ve mağaza isimlerinde sık kullanılıyor"),
]
ILK10 = [ad for ad, *_ in ILK50[:10]]


def raporla():
    havuz = topla()
    ilk50 = {ad: (i + 1, p, n, d) for i, (ad, p, n, d) in enumerate(ILK50)}
    satirlar = []
    for ad, bilgi in havuz.items():
        g = gerekce(ad)
        tur = "1. tur" if g else ""
        if not g:
            g2 = ikinci_tur(ad, bilgi)
            if g2:
                g, tur = g2, "2. tur"
        if not g and ad not in ilk50:
            g = "12. Üçüncü tur (tek tek değerlendirme): " + TUR3.get(ad, "İlk 50'ye giremedi")
            tur = "3. tur"
        if ad in ilk50:
            sira = ilk50[ad][0]
            durum = "İLK 10" if sira <= 10 else "İLK 50"
            satirlar.append({"isim": ad, "aile": bilgi["aile"], "kaynak": bilgi["kaynak"], "hece": hece(ad),
                             "durum": durum, "sira": sira, "tur": "", "gerekce": ilk50[ad][2]})
        else:
            satirlar.append({"isim": ad, "aile": bilgi["aile"], "kaynak": bilgi["kaynak"], "hece": hece(ad),
                             "durum": "elendi", "sira": "", "tur": tur, "gerekce": g})
    return satirlar


def yaz():
    OUT.mkdir(parents=True, exist_ok=True)
    satirlar = raporla()
    with open(OUT / "havuz.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(satirlar[0].keys()))
        w.writeheader()
        w.writerows(satirlar)
    # Gerekçeye göre gruplu eleme listesi
    gruplar = OrderedDict()
    for s in satirlar:
        if s["durum"] != "elendi":
            continue
        anahtar = re.sub(r" \(.*", "", s["gerekce"].split(":")[0])
        gruplar.setdefault(anahtar, []).append(s)
    with open(OUT / "eleme-listesi.md", "w", encoding="utf-8") as fh:
        fh.write("# Eleme Listesi: her isim ve elenme gerekçesi\n\n")
        fh.write(f"Toplam aday: **{len(satirlar)}** · Elenen: **{sum(1 for s in satirlar if s['durum']=='elendi')}** · İlk 50: **50**\n\n")
        fh.write("> Tüm veriler `havuz.csv` dosyasında da var (isim, aile, kaynak, hece, durum, tur, gerekçe).\n\n")
        for anahtar in sorted(gruplar, key=lambda k: int(k.split(".")[0])):
            liste = gruplar[anahtar]
            fh.write(f"## {anahtar} ({len(liste)} isim)\n\n")
            ozel = any(":" in s["gerekce"] and len(s["gerekce"].split(":", 1)[1].strip()) > 0 and anahtar.split(".")[0] in ("2", "4", "12") for s in liste)
            if anahtar.startswith("6."):
                fh.write("Antre ve Radyal 2 hece; en fazla 3 hece ve 9 harf hedeflendi.\n\n| İsim | Hece / harf |\n|---|---|\n")
                for s in liste:
                    fh.write(f"| {s['isim']} | {s['hece']} hece, {len(s['isim'])} harf |\n")
            elif ozel:
                fh.write("| İsim | Gerekçe |\n|---|---|\n")
                for s in liste:
                    fh.write(f"| {s['isim']} | {s['gerekce'].split(':', 1)[1].strip()} |\n")
            else:
                fh.write(liste[0]["gerekce"].split(":", 1)[1].strip() + "\n\n")
                fh.write(", ".join(s["isim"] for s in liste) + "\n")
            fh.write("\n")
    sayac = Counter(s["tur"] or s["durum"] for s in satirlar)
    print(len(satirlar), dict(sayac))
    eksik = [ad for ad, *_ in ILK50 if ad not in {s["isim"] for s in satirlar}]
    print("ilk50'de havuzda olmayan:", eksik)


if __name__ == "__main__":
    yaz()
