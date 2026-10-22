# Artvela Türk Sanatçılar Arşivi: Kabul Ölçütleri ve Puanlama Sistemi

Sürüm 0.1 · 2026-10-22

## 1. Arşive kimler girer?

Bir sanatçı, aşağıdaki üç kapıdan **en az birinden** geçiyorsa arşive alınır. Geçtiği kapı her dosyada `kabul` alanına yazılır.

| Kapı | Ölçüt | Kanıt örneği |
|---|---|---|
| **K1 · Akademik** | Bir güzel sanatlar akademisinden ya da fakültesinden (resim, heykel, baskı, seramik, grafik) mezun olmuş. Yurtiçi ya da yurtdışı fark etmez. | Mezuniyet yılı, atölye hocası |
| **K2 · Galeri** | Kurumsal bir galeriyle düzenli çalışmış ya da böyle bir galeride kişisel sergi açmış. | Galeri adı, sergi yılı |
| **K3 · Otorite onayı** | Akademi dışından geliyor ama sanat otoritelerinden geçerli not almış: müze koleksiyonuna girmiş, kurumsal bir ödül almış, müze ya da kurum sergisi açılmış, hakkında tez, monografi ya da eleştiri yazılmış. | Koleksiyon, ödül, tez künyesi |

**Arşive girmeyenler:** Hobi düzeyinde üretenler, yalnızca sosyal medyada ya da ticari dekorasyon kanalında görünenler, kanıtı yalnızca kendi beyanına dayananlar.

## 2. Puanlama (100 puan)

Puan, sanatçının **kurumsal ve tarihsel ağırlığını** ve **piyasa görünürlüğünü** birlikte ölçer. Beş boyuttan oluşur:

### A. Eğitim ve akademik geçerlilik: 15 puan
| Alt ölçüt | Puan |
|---|---|
| Akademi ya da fakülte mezunu | 0–8 |
| Yurtdışında eğitim, burs ya da rezidans | 0–4 |
| Akademisyenlik, atölye hocalığı ya da öğrenci yetiştirme | 0–3 |

### B. Sergi geçmişi: 25 puan
| Alt ölçüt | Puan |
|---|---|
| Kişisel sergilerin sayısı ve niteliği (kurumsal galeri, düzenlilik) | 0–10 |
| Retrospektif ya da müze ve kurum sergisi | 0–8 |
| Uluslararası sergi, salon, bienal ya da fuar | 0–7 |

### C. Kurumsal tanınırlık: 20 puan
| Alt ölçüt | Puan |
|---|---|
| Türkiye'deki müze koleksiyonları (İstanbul Modern, İRHM, devlet resim heykel müzeleri, özel müzeler) | 0–8 |
| Yurtdışındaki müze ve kurum koleksiyonları | 0–7 |
| Ödüller (devlet, DYO, Sedat Simavi, uluslararası) | 0–5 |

### D. Sanat tarihindeki konum: 15 puan
| Alt ölçüt | Puan |
|---|---|
| Bir grubun ya da akımın kurucusu veya öncüsü, bir kuşağın temsilcisi | 0–8 |
| Hakkında akademik yayın, tez, monografi, kendi adını taşıyan müze | 0–7 |

### E. Piyasa görünürlüğü: 25 puan
| Alt ölçüt | Puan |
|---|---|
| Türk müzayedelerindeki düzenli varlığı (Artvela dahil) | 0–8 |
| Uluslararası müzayedelerdeki varlığı (Sotheby's, Christie's, Bonhams, Drouot vb.) | 0–7 |
| Fiyat seviyesi (doğrulanmış satışlara göre) | 0–6 |
| Güncel galeri temsili | 0–4 |

## 3. Kademeler

| Puan | Kademe | Anlamı (Artvela için) |
|---|---|---|
| 80–100 | **I · Kanonik** | Türk sanat tarihinin ana omurgası. Seçkinin "vitrin" eserleri. |
| 60–79 | **II · Yerleşik** | Kurumsal olarak kabul görmüş, piyasası oturmuş. Müzayedenin gövdesi. |
| 40–59 | **III · Güçlü orta** | Akademik ve kurumsal zemini sağlam, piyasası gelişen. Keşif ve değer fırsatı. |
| 20–39 | **IV · Gelişen** | Kabul ölçütlerini karşılıyor ama veri ya da görünürlük sınırlı. |
| 0–19 | **V · İzleme** | Arşivde, ama puan vermek için veri yetersiz. |

## 4. Veri kapsamı kuralı (önemli)

- Her alt puanın yanında **kanıt** ve **kaynak** yazılır. Kanıtı olmayan alt ölçüt 0 alır ve `eksik` olarak işaretlenir. Puan uydurulmaz.
- Her dosyada **veri kapsamı** belirtilir: puanlanabilen alt ölçüt sayısının toplam alt ölçüt sayısına (15) oranı.
- Veri kapsamı %70'in altındaysa puan **"ön puan"** sayılır ve kademe parantez içinde gösterilir, örneğin "(II)". Ön puan sanatçının gerçek ağırlığını *düşük* gösterebilir. Bunun nedeni sanatçının zayıflığı değil, verinin henüz girilmemiş olmasıdır.
- **E boyutundaki fiyat puanı** yalnızca doğrulanmış satış kayıtlarıyla verilir (müzayede evi arşivi, katalog, fiyat veritabanı).

## 5. Güncelleme döngüsü

1. Yeni sanatçı: kabul kapısı kontrol edilir → `sanatcilar/<slug>.md` dosyası açılır → `sanatcilar.csv`'ye satır eklenir.
2. Mevcut sanatçı: yeni sergi, satış ya da koleksiyon bilgisi geldikçe ilgili alt puan güncellenir, `son_guncelleme` değişir.
3. Her müzayede öncesinde lotlardaki sanatçıların dosyaları gözden geçirilir. Bölüm 5 (eser analizi) ve bölüm 6 (piyasa verisi) doldurulur.
