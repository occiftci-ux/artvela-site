# Sabah Raporu: Galeri İsmi Gece Çalışması

> Hazırlanma: 17 Ekim 2026, gece (Türkiye saatiyle 02.45 civarı başladı)
> Kaynak betik: `scripts/isim_eleme.py` · Tüm adaylar: `havuz.csv` · Gerekçeli eleme listesi: `eleme-listesi.md`

## Kısaca
- **1.215 aday** değerlendirildi: önceki turlardan 1.008 isim ve bu gece yeni üretilen 207 isim.
- Elemeler **üç turda** yapıldı. **Her elenen ismin gerekçesi** `eleme-listesi.md` ve `havuz.csv` dosyalarında kayıtlı.
- **İlk 50** aşağıda; her ismin neden seçildiği ve nelere dikkat edilmesi gerektiği yazıyor.
- **İlk 10** için özgünlük taraması yapıldı. Domain kayıt durumunu **doğrudan sorgulayamadım** (aşağıda nedenini yazdım).

## Seçim ölçütleri
Beğendiğiniz isimler (Antre, Radyal, Bediz, Bej, Opak, Meridyen) şu profili verdi:
1. **Kısa:** 1–3 hece; Antre ve Radyal 2 hece.
2. **Türkçeleşmiş yabancı kelime:** Fransızca ya da Latince kökenli ama Türkçe yazılan, gündelik dilde yaşayan kelimeler.
3. **Yan yoldan anlam:** "Sanat" demeden mekân, yön, yüzey, iz ya da ilk adım anlatan kelimeler.
4. **Gizli hikâye:** Sorulduğunda galerinin yapısını (aynı binada iki marka, genç sanatçılar, yayıncılık, figür) anlatabilen kelimeler.
5. **Ayırt edicilik:** Türkiye'de isim, marka ya da olumsuz bir deyim olarak yerleşmemiş olmak.

Puanlama, her ölçüt için 1–5 arası olmak üzere 25 üzerinden yapıldı.

## Eleme turları
| Tur | Kural | Elenen |
|---|---|---|
| 1 | Birden çok kelime | 37 |
| 1 | Bilinen benzerlik ya da çakışma (aramalarda bulunanlar ve büyük markalar) | 36 |
| 1 | Türkiye'de yaygın kişi adı | 42 |
| 1 | Olumsuz, uygunsuz ya da yanlış yönlendiren çağrışım (her biri için ayrı gerekçe) | 141 |
| 1 | Türkçe yazımı yok (Antre ve Radyal çizgisi Türkçeleşmiş kelimeler) | 75 |
| 1 | Uzun (3 heceden ya da 9 harften fazla) | 73 |
| 1 | Bir sanat akımının adı | 8 |
| 1 | Betimleyici ya da jenerik sanat kelimesi (tescil ve ayırt edicilik zayıf) | 102 |
| 2 | Osmanlıca ya da klasik ağırlık (modern ve sade çizgiye uzak) | 77 |
| 2 | Çok gündelik ya da dar teknik kelime | 246 |
| 2 | Antre ve Radyal çizgisine uzak (çoğu önceki turlarda size sunulup beğenilmemiş isimler) | 184 |
| 3 | Tek tek değerlendirme (144 isim, her biri için ayrı gerekçe) | 144 |
| | **İlk 50'ye kalan** | **50** |

## İlk 10: özgünlük ve domain kontrolü
**Domain notu:** Bu çalışma ortamının ağ politikası domain kayıt sistemlerine erişime izin vermiyor. rdap.org, rdap.verisign.com, nic.tr, whois.com, dns.google ve cloudflare-dns.com reddedildi; normal DNS çözümlemesi de çalışmıyor. Bu yüzden "boş" ya da "dolu" diye kesin bir sonuç **veremiyorum**; tahmin de yazmadım.

Aşağıdaki "web izi" sütunu, web aramasında o isimle bir site, galeri ya da marka görünüp görünmediğini gösteriyor. Bilinen bir genel kural: tek kelimelik sözlük kelimelerinin `.com` uzantıları büyük çoğunlukla yıllar önce kayıt edilmiştir. Bu nedenle bileşik biçimler (`galeriparaf.com`, `paraf.gallery` gibi) daha gerçekçi seçeneklerdir.

| # | İsim | Türkiye'de benzerlik | Dünyada benzerlik | Kontrol edilecek domainler |
|---|---|---|---|---|
| 1 | **Paraf** | Galeri ya da marka çıkmadı | Paris'te çıkmadı | paraf.com.tr · paraf.art · paraf.gallery · galeriparaf.com · parafgallery.com |
| 2 | **Antresol** | Galeri ya da marka çıkmadı | Yalnızca mimari terim olarak geçiyor | antresol.com · antresol.com.tr · antresol.art · antresol.gallery |
| 3 | **Guaj** | Çıkmadı | Çıkmadı | guaj.com · guaj.com.tr · guaj.art · guaj.gallery · galeriguaj.com |
| 4 | **Etaj** | Çıkmadı | ⚠ Berlin'de "GalerieETAGE", Paris'te kapanmış "5ème Etage" (yazımları farklı) | etaj.com.tr · etaj.art · etaj.gallery · galerietaj.com |
| 5 | **Antre** ★ | ⚠ İstanbul'da "Antrepo" adlı bir sanat mekânı var (ses yakınlığı) | Çıkmadı | antre.com.tr · antre.art · antre.gallery · galeriantre.com |
| 6 | **Radyal** ★ | Galeri çıkmadı; ⚠ "radyal lastik" ifadesi çok yaygın (genel bilgi) | Çıkmadı | radyal.com · radyal.com.tr · radyal.art · radyal.gallery |
| 7 | **Bediz** ★ | ⚠ Türkiye'nin ilk profesyonel fotoğrafçısı Bahaettin Rahmi Bediz'in soyadı; Karaköy'de "Bediz Clothing" adlı bir tekstil firması kaydı var | Çıkmadı | bediz.com · bediz.com.tr · bediz.art · bediz.gallery |
| 8 | **Vual** | Çıkmadı | Paris'te "Galerie VU'" adlı fotoğraf galerisi var (ses benzerliği zayıf) | vual.com · vual.com.tr · vual.art · vual.gallery |
| 9 | **Ajur** | Çıkmadı | Çıkmadı | ajur.com · ajur.com.tr · ajur.art · ajur.gallery |
| 10 | **Fokal** | Çıkmadı | ⚠ Varşova'daki ünlü "Foksal Gallery" ile tek harf fark | fokal.com.tr · fokal.art · fokal.gallery · galerifokal.com |

**Bu gece ilk 10'dan çıkarılan iki isim:**
- **Ekru:** Türkiye'de sesi neredeyse aynı olan 60 mağazalı "Ecrou" perakende zinciri var.
- **Estamp:** Madrid'de "Estampa" sanat fuarı ve "Galería Estampa" var.

**Domainleri sizin kontrol etmeniz için en hızlı yol:**
- `.com.tr` ve `.tr` uzantıları için nic.tr'deki TRABİS sorgusu
- `.com`, `.art` ve `.gallery` uzantıları için herhangi bir domain kayıt firmasının arama kutusu

**Marka için:** Domain kadar önemli olan TÜRKPATENT marka araştırması. Sınıf 35 (perakende ve satış), sınıf 41 (sergi ve kültürel faaliyet) ve sınıf 16 (basılı yayın) kontrol edilmeli.

## İlk 50
★ = sizin önerdiğiniz ya da beğendiğiniz isim

| Sıra | İsim | Puan | Neden seçildi | Dikkat |
|---|---|---|---|---|
| 1 | **Paraf** | 24/25 | İmzanın baş harflerle atılan kısa hâli: sanatçının işareti. İki heceli, Fransızca kökenli ama Türkçede yaşayan bir kelime; Antre ile aynı tını. Galerinin 'onayladığı' sanatçı fikrini taşıyor | Gece taramasında Türkiye'de ve Paris'te galeri ya da marka çıkmadı |
| 2 | **Antresol** | 24/25 | 'Katlar arası': zemin ile birinci kat arasındaki ara kat. Aynı binada iki ayrı markanın (müzayede ve galeri) olacağı yapıya birebir uyuyor. Antre'nin kardeşi | Gece taramasında galeri çıkmadı; Fransızca 'entresol' yalnızca mimari terim olarak geçiyor |
| 3 | **Guaj** | 23/25 | Guaş: opak suluboya. Opak'ın akrabası, tek hece, yabancıların da okuyabileceği bir ses (gwaş). Figür ve desen geleneğinin malzemesi | Gece taramasında galeri ya da marka çıkmadı |
| 4 | **Etaj** | 23/25 | Fransızca 'étage', yani kat. Kısa, karakterli 'j' harfi (Bej gibi). Galerinin binadaki yerini sade bir kelimeyle söylüyor | Berlin'de 'GalerieETAGE', Paris'te kapanmış '5ème Etage' var; yazım farklı, risk hafif |
| 5 | **Antre** ★ | 22/25 | Sizin seçiminiz. 'Giriş': galerisi olmayan yetenekler için giriş kapısı | İstanbul'da 'Antrepo' adlı bir sanat mekânı var; ses yakınlığı riski |
| 6 | **Radyal** ★ | 22/25 | Sizin seçiminiz. 'Merkezden dışa yayılan': bir merkezden sanatın yayılması | Türkiye'de 'radyal lastik' ifadesi çok yaygın; otomotiv çağrışımı riski |
| 7 | **Bediz** ★ | 22/25 | Sizin beğendiğiniz. Göktürkçede 'resim, süs'; Türk resim dilinin bilinen en eski kelimesi | Türkiye'nin ilk profesyonel fotoğrafçısı Bahaettin Rahmi Bediz'in soyadı; Karaköy'de 'Bediz Clothing' adlı bir tekstil firması kaydı var |
| 8 | **Vual** | 23/25 | Fransızca 'voile', yani peçe: resmin üstüne çekilen ince, saydam katman. Tek hece, yumuşak ve modern | Paris'te fotoğraf galerisi 'Galerie VU'' var; ses benzerliği zayıf |
| 9 | **Ajur** | 23/25 | Işığın içinden geçtiği delikli işleme. Işık ile doku tek kelimede; iki hece, 'j' harfi | Gece taramasında galeri ya da marka çıkmadı |
| 10 | **Fokal** | 22/25 | 'Odaksal': bakışın toplandığı nokta. Radyal ile aynı ailede, iki heceli | Varşova'daki ünlü 'Foksal Gallery' ile tek harf fark; sanat dünyasında karışma riski |
| 11 | **Debü** | 22/25 | İlk çıkış, ilk sergi. Genç sanatçılara ilk kapıyı açan bir galeri için birebir | 'ü' harfi yabancılar için zor; uluslararası yazımda 'Debu' olur |
| 12 | **Opak** ★ | 22/25 | Sizin öneriniz. Işığı geçirmeyen, yoğun yüzey; Guaj'ın da niteliği | Sert ve sade; ön taramada sorun bilinmiyor |
| 13 | **Kolofon** | 22/25 | Eski kitapların son sayfasındaki basım notu. Yunanca anlamı 'son dokunuş'; yayıncı galeri için güçlü | Üç hece; kitap dünyası dışında az bilinir |
| 14 | **Filigran** | 22/25 | Kâğıdın içine gömülü, ışığa tutunca görünen damga: görünmez kalite işareti | Üç hece; kuyum sektöründe 'telkâri' anlamında da kullanılır |
| 15 | **Muare** | 22/25 | Kumaşta ve baskıda dalga dalga parıltı (moiré). Yumuşak ve özgün bir ses | 'ua' ses dizisi yabancı okuyucu için belirsiz |
| 16 | **Glase** | 22/25 | Sırlı ve parlak (glacé); resimde 'glaze', yani şeffaf sır katmanı | 'Glase kestane' ve 'glase deri' çağrışımı |
| 17 | **Rakurs** | 22/25 | Perspektifte figürü kısaltarak çizmek: figüratif resmin en zor tekniği | Sert bir ses; sanat dışında bilinmiyor |
| 18 | **Tiraj** | 22/25 | Bir yayının baskı adedi. Yayıncı galeri ve edisyon fikri | Gazete satış rakamlarını çağrıştırır |
| 19 | **Vinyet** | 22/25 | Kenarları silikleşen küçük resim: dikkati merkeze çeken çerçeve | 'Vinyet' sigara paketlerindeki etiket anlamıyla da kullanılır |
| 20 | **Parter** | 22/25 | Zemin kat ve Fransız bahçesi: binanın sokağa açılan katı | Tiyatroda 'parter' salonu; spor 'partner' ile karışabilir |
| 21 | **Fuaye** | 22/25 | Tiyatronun giriş salonu: buluşma, sohbet ve ilk izlenim yeri | Tiyatro çağrışımı güçlü |
| 22 | **Repriz** | 22/25 | Yeniden sahneleme: ustaların yeniden keşfi fikri | 'Repriz' sinema ve televizyonda tekrar yayın anlamında |
| 23 | **Kadans** | 22/25 | Ritim, ölçü ve kapanış cümlesi: düzenli bir sergi programının metaforu | Müzik dışında az bilinir |
| 24 | **Fermata** | 21/25 | Müzikte notayı uzatma işareti (𝄐): zamanın durduğu an. Logosu hazır | İtalyanca; üç hece |
| 25 | **Radyan** | 21/25 | Açı birimi; sesi 'radiant', yani ışıldayan. Radyal'in kardeşi | Radyal ile aynı ses ailesi; matematik çağrışımı |
| 26 | **Aksiyal** | 21/25 | Eksen boyunca: bir çizgiye bağlılık, programın ekseni | Üç hece; teknik |
| 27 | **Verso** | 21/25 | Bir resmin arka yüzü: provenans etiketleri ve tarihin saklandığı yer | Çok sayıda yabancı markada kullanılıyor |
| 28 | **Avan** | 21/25 | 'Önce, ön'; mimarlıkta 'avan proje', yani ilk tasarım | 'Avangart' kısaltması gibi okunabilir |
| 29 | **Kaşe** | 21/25 | Üç anlamı var: mühür, sanatçıya ödenen ücret ve 'kaşesi var' deyimindeki prestij | 'ş' harfi; ilaç kaşesi çağrışımı |
| 30 | **Faktür** | 21/25 | Resimde boyanın yüzeyde işlenişi; ressamın el izi | Muhasebede 'fatura' anlamıyla karışabilir |
| 31 | **Gnomon** | 21/25 | Güneş saatinin gölge düşüren çubuğu: gölgeyle zaman yazan alet. Resmin gölgeden doğduğu efsaneyle bağı var | 'Gn' ile başlıyor; Türkçede okunuşu yabancı |
| 32 | **Albedo** | 21/25 | Bir yüzeyin ışığı yansıtma oranı: bilimsel ve sade | İngiltere'de 'Albedo Marz' adlı bir sanatçı var |
| 33 | **Zenit** | 21/25 | Göğün tepe noktası, doruk | Zenit fotoğraf makinesi ve Zenit futbol kulübü |
| 34 | **Mezanin** | 21/25 | Asma kat; Antresol'un İtalyanca kökenli eşi | Mimari jargon; restoranlarda da kullanılır |
| 35 | **Atik** | 21/25 | Çatı katı, ayrıca Türkçede 'çevik, tetik': çift anlam | 'Atik' bazı soyadlarında var |
| 36 | **Düble** | 21/25 | 'Çift' ve altın kaplama: aynı binada iki marka fikri | 'Düble rakı' çağrışımı |
| 37 | **Velur** | 21/25 | Kadife: yumuşak bir ses ve dokunsal bir anlam | Tekstil sektöründe ürün adı |
| 38 | **Görk** | 21/25 | Eski Türkçede 'güzellik', görkem kelimesinin kökü. Bediz ailesinden, tek hece | 'ö' harfi; anlamı açıklama ister |
| 39 | **Lineer** | 20/25 | Çizgisel: desen ve çizgi geleneği | Matematik ve 'lineer cebir' çağrışımı |
| 40 | **Sagital** | 20/25 | Bedeni ikiye bölen düzlem; kökü Latince 'ok' | Anatomi jargonu |
| 41 | **Boreal** | 20/25 | Kuzeye ait; 'aurora borealis', yani kuzey ışıkları | Bazı yabancı markalarda kullanılıyor |
| 42 | **Antrakt** | 20/25 | İki perde arasındaki an; Antre'nin akrabası | 'kt' ile bitiş sert |
| 43 | **Paspartu** | 20/25 | Resmin çevresindeki karton; kelimenin anlamı 'her kapıyı açan' | Üç hece; çerçeveci dükkânlarında kullanılır |
| 44 | **Kontrjur** | 20/25 | Işığa karşı çekim: figürü arkadan gelen ışıkla göstermek | Okunuşu zor |
| 45 | **Lünet** | 20/25 | Kemer altındaki yarım daire resim | 'ü' harfi |
| 46 | **Seladon** | 20/25 | Topkapı'nın koleksiyonuyla ünlü yeşimsi seramik yeşili | Üç hece; renk adı olarak az bilinir |
| 47 | **Nötr** | 19/25 | Tarafsız renk; müzayededen bağımsız bir galerinin sessiz metaforu | 'ö' harfi ve ünsüz kümesi |
| 48 | **Tonal** | 19/25 | Tona ait: renk ve ışık ilişkisi | Sıfat; tek başına zayıf |
| 49 | **Meridyen** ★ | 19/25 | Sizin öneriniz. Boylam çizgisi, yani yeryüzünü bölen ince çizgi | Le Méridien otel zinciri ile güçlü çağrışım; Türkiye'de çok sayıda 'Meridyen' işletmesi |
| 50 | **Bej** ★ | 18/25 | Sizin öneriniz. En sade renk adı | Çok yaygın bir renk adı; kafe ve mağaza isimlerinde sık kullanılıyor |

## Benim önerim
1. **Paraf**: en temiz ön tarama sonucu ve en güçlü gizli anlam. İmza, yani "bu sanatçıyı biz onaylıyoruz". Antre ile aynı tını, iki hece, uluslararası okunabilir.
2. **Antresol**: aynı binada iki marka (müzayede ve galeri) yapısını tek kelimeyle anlatıyor. Galeri "katlar arasında", kendi katında.
3. **Guaj**: Opak'ın akrabası, tek hece, figür ve desen geleneğinin malzemesi.

**Sıradaki adımlar:**
1. Bu üç ismin ve Antre ile Radyal'in domainlerini kontrol etmek: kendiniz bakabilirsiniz ya da ortamın ağ izinlerini açarsanız ben bakarım.
2. TÜRKPATENT marka araştırması.
3. Kısa bir logo ve tipografi denemesi.

## Kaynaklar (gece taraması)
- [Kariyer.net – Ecrou Mağazacılık](https://www.kariyer.net/firma-profil/ecrou-magazaclik-a-s-6553-496376) · [Para Dergi – Ecrou](https://www.paradergi.com.tr/is-dunyasi-kulis/2025/04/03/perakende-gurusunun-bas-donduren-yukselisi)
- [IFEMA – Estampa](https://www.ifema.es/estampa/catalogo/galeria-estampa/)
- [Wikipedia – Bahaettin Rahmi Bediz](https://en.wikipedia.org/wiki/Bahaettin_Rahmi_Bediz) · [Textile Infomedia – Bediz Clothing](https://www.textileinfomedia.com/business-info/Bediz-Clothing)
- [Comité des galeries d'art – Galerie VU'](https://www.comitedesgaleriesdart.com/en/galeries/galerie-vu/)
- [Foksal Gallery](https://en.wikipedia.org/wiki/Foksal_Gallery)
- [KGBerlin – GalerieETAGE](https://kgberlin.net/en/galleries/galerieetage-im-museum-reinickendorf/) · [e-flux – 5ème Etage](https://www.e-flux.com/directory/69739/5me-etage/)
- [Frommer's – İstanbul galerileri (Antrepo)](https://www.frommers.com/destinations/istanbul/things-to-do/art-galleries/)
