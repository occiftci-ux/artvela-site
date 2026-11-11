#!/bin/bash
# Lebriz koruma turu (2026-11-05'ten beri: yeni dosyalar yerel diske, paketler WebDAV sunucusuna; proje deposu dolmaz).
# Bağlantı kuralı: lebriz.com'a tek bağlantı (crawl.py), lebrizImages.net'e iki bağlantı (gorsel_cek.py x2, L3 onayı 11 Kasım). Engel çıkarsa dur.
# Gerekli: ONUR_SUNUCU_ANAHTAR ortam sırrı. Eski paketler sunucudan ~/lebriz-onbellek'e indirilerek okunur.
K=/mnt/project-files/arastirma/sanat-tarihi/lebriz/koruma; A=/mnt/project-files/arastirma/sanat-tarihi/lebriz/araclar
: "${ONUR_SUNUCU_ANAHTAR:?ONUR_SUNUCU_ANAHTAR ortam sırrı yok}"
export LEBRIZ_YEREL=${LEBRIZ_YEREL:-$HOME/lebriz-yerel} LEBRIZ_ONBELLEK=${LEBRIZ_ONBELLEK:-$HOME/lebriz-onbellek}
cd /tmp
# Önceki tur konteyner yeniden başlayınca yarıda kaldıysa, yerelde bekleyenleri önce sunucuya gönder.
[ -n "$(find "$LEBRIZ_YEREL" -type f -not -name '*.tmp' 2>/dev/null | head -1)" ] && timeout 3600 python3 -I $A/paketle.py $K /tmp/lebriz-paket --sil
# müzayede bankası bitti (10.029/10.029, 2026-11-05):
# NODE_PATH=$(npm root -g) DELAY_MS=1000 node $A/muzayede_cek.js $K 0.8
# 2026-11-08 sahip: hızlandır, bir an önce bitir. Tur 1,5 saat (Bash arka plan görevi 2 saatte kesilir; setsid ile ayrılan süreçler konteyner boşta kalınca ölüyor), görsel aralığı kısaldı; yine sunucu başına tek bağlantı.
DELAY=${SAYFA_DELAY:-1.0} python3 -I $K/crawl.py $K ${SAYFA_SAAT:-1.25} $K/seeds.txt &
# 2026-11-11 sahip L3 onayı: lebrizImages.net'e ikinci bağlantı. İkinci süreç yalnız kalıcı kuyruğun (bekleyen.tsv) öbür yarısını indirir.
GORSEL_BOLUM=0/2 DELAY=${GORSEL_DELAY:-0.3} python3 -I $A/gorsel_cek.py $K ${GORSEL_SAAT:-1.25} &
GORSEL_BOLUM=1/2 SADECE_BEKLEYEN=1 DELAY=${GORSEL_DELAY:-0.3} python3 -I $A/gorsel_cek.py $K ${GORSEL_SAAT:-1.25} &
wait
# Tur sonunda yerel dosyaları doğrulayarak zip'le, sunucuya yükle, geri indirip doğrula, ancak sonra sil.
timeout 3600 python3 -I $A/paketle.py $K /tmp/lebriz-paket --sil
