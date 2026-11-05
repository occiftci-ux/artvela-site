#!/bin/bash
# Lebriz koruma turu (2026-11-05'ten beri: yeni dosyalar yerel diske, paketler WebDAV sunucusuna; proje deposu dolmaz).
# Bağlantı kuralı: lebriz.com'a tek bağlantı (crawl.py), lebrizImages.net'e tek bağlantı (gorsel_cek.py). Engel çıkarsa dur.
# Gerekli: ONUR_SUNUCU_ANAHTAR ortam sırrı. Eski paketler sunucudan ~/lebriz-onbellek'e indirilerek okunur.
K=/mnt/project-files/arastirma/sanat-tarihi/lebriz/koruma; A=/mnt/project-files/arastirma/sanat-tarihi/lebriz/araclar
: "${ONUR_SUNUCU_ANAHTAR:?ONUR_SUNUCU_ANAHTAR ortam sırrı yok}"
export LEBRIZ_YEREL=${LEBRIZ_YEREL:-$HOME/lebriz-yerel} LEBRIZ_ONBELLEK=${LEBRIZ_ONBELLEK:-$HOME/lebriz-onbellek}
cd /tmp
# müzayede bankası bitti (10.029/10.029, 2026-11-05):
# NODE_PATH=$(npm root -g) DELAY_MS=1000 node $A/muzayede_cek.js $K 0.8
DELAY=1.0 python3 -I $K/crawl.py $K 1.3 $K/seeds.txt &
DELAY=1.0 python3 -I $A/gorsel_cek.py $K 1.8 &
wait
# Tur sonunda yerel dosyaları doğrulayarak zip'le, sunucuya yükle, geri indirip doğrula, ancak sonra sil.
timeout 3600 python3 -I $A/paketle.py $K /tmp/lebriz-paket --sil
