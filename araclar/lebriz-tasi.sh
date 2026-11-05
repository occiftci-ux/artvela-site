#!/usr/bin/env bash
# Lebriz koruma paketlerini proje deposundan WebDAV sunucusuna taşır.
# Her zip: yerel kopya -> sha256 -> 90 MB parçalara böl -> yükle -> geri indir,
# sha256 karşılaştır -> hepsi tutarsa proje deposundaki asıl dosyayı sil.
# Kullanım: ONUR_SUNUCU_ANAHTAR=... bash lebriz-tasi.sh [kaynak_klasor]
set -euo pipefail

KAYNAK="${1:-/mnt/project-files/arastirma/sanat-tarihi/lebriz/koruma}"
DAV="https://ocal.galeribej.com/lebriz-depo"
KULLANICI="ocal-lebriz"
UZAK_KLASOR="koruma"                 # sunucuda: /lebriz-depo/koruma/<zip-adi>/<parca>
IS="${IS_KLASORU:-$HOME/lebriz-tasi}" # yerel çalışma alanı (proje deposu değil)
DIZIN="$IS/sunucu-dizini.tsv"        # sha256 dizini; her adımdan sonra sunucuya da yüklenir
GUNLUK="$IS/gunluk.txt"
PARCA="${PARCA:-20M}"   # Cloudflare 100 sn sınırı: hat ~0,5-2 MB/sn, 90M zaman aşımına düşüyor
PARALEL="${PARALEL:-4}"

: "${ONUR_SUNUCU_ANAHTAR:?ONUR_SUNUCU_ANAHTAR ortam sırrı yok}"
mkdir -p "$IS/tmp"
NETRC="$IS/.netrc"; umask 077
printf 'machine ocal.galeribej.com login %s password %s\n' "$KULLANICI" "$ONUR_SUNUCU_ANAHTAR" > "$NETRC"
umask 022
C=(curl -sS --fail --retry 4 --retry-delay 5 --netrc-file "$NETRC")

log(){ echo "$(date -u +%FT%TZ) $*" | tee -a "$GUNLUK"; }
mkcol(){ "${C[@]}" -o /dev/null -X MKCOL "$DAV/$1/" 2>/dev/null || true; }

[ -f "$DIZIN" ] || printf 'dosya\ttoplam_bayt\tsha256\tparca_sayisi\tparca\tparca_bayt\tparca_sha256\tuzak_yol\ttarih\n' > "$DIZIN"
mkcol "$UZAK_KLASOR"

for z in "$KAYNAK"/paket-*.zip; do
  [ -e "$z" ] || continue
  ad=$(basename "$z")
  log "BAŞLA $ad"
  rm -rf "$IS/tmp"/*; cp "$z" "$IS/tmp/$ad"
  boy=$(stat -c%s "$IS/tmp/$ad")
  [ "$boy" = "$(stat -c%s "$z")" ] || { log "HATA kopya boyutu $ad"; continue; }
  sha=$(sha256sum "$IS/tmp/$ad" | cut -d' ' -f1)
  ( cd "$IS/tmp" && split -b "$PARCA" -d -a 3 "$ad" "$ad.part" )
  parcalar=( "$IS/tmp/$ad".part[0-9][0-9][0-9] ); n=${#parcalar[@]}
  mkcol "$UZAK_KLASOR/$ad"
  satirlar=""; tamam=1
  export DAV NETRC IS
  printf '%s\n' "${parcalar[@]}" | xargs -P "$PARALEL" -I{} bash -c '
    p="$1"; pa=$(basename "$p"); ad=${pa%.part*}; yol="koruma/$ad/$pa"
    ps=$(sha256sum "$p" | cut -d" " -f1)
    for d in 1 2 3; do
      curl -sS --fail --retry 4 --retry-delay 5 --netrc-file "$NETRC" -o /dev/null -T "$p" "$DAV/$yol" \
      && gs=$(curl -sS --fail --retry 4 --retry-delay 5 --netrc-file "$NETRC" "$DAV/$yol" | sha256sum | cut -d" " -f1) \
      && [ "$gs" = "$ps" ] && { echo "$pa	$(stat -c%s "$p")	$ps	/lebriz-depo/$yol" > "$p.ok"; exit 0; }
      sleep 10
    done; exit 1' _ {} || true
  satirlar=""; tamam=1
  for p in "${parcalar[@]}"; do
    if [ -f "$p.ok" ]; then
      IFS=$'\t' read -r pa pb ps yol < "$p.ok"
      satirlar+="$ad	$boy	$sha	$n	$pa	$pb	$ps	$yol	$(date -u +%FT%TZ)"$'\n'
    else log "HATA yükleme/doğrulama $(basename "$p")"; tamam=0; fi
  done
  if [ "$tamam" = 1 ]; then
    # birleşik sha256 de tutmalı
    bs=$(cat "${parcalar[@]}" | sha256sum | cut -d' ' -f1)
    [ "$bs" = "$sha" ] || { log "HATA birleşik sha $ad"; continue; }
    printf '%s' "$satirlar" >> "$DIZIN"
    "${C[@]}" -o /dev/null -T "$DIZIN" "$DAV/sunucu-dizini.tsv"
    rm -f "$z"
    log "TAMAM $ad $n parça, kaynak silindi"
  fi
  rm -rf "$IS/tmp"/*
done
# yardımcı dosyalar (paketler.tsv, manifestler) kopya olarak gider, depoda kalır
for f in paketler.tsv manifest.tsv; do
  [ -f "$KAYNAK/$f" ] && "${C[@]}" -o /dev/null -T "$KAYNAK/$f" "$DAV/$UZAK_KLASOR/$f" && log "KOPYA $f"
done
rm -f "$NETRC"
log "BİTTİ"
