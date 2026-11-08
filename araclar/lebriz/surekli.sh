#!/bin/bash
# Lebriz turlarını art arda çalıştırır (sahip 2026-11-08: en kısa sürede bitir). Kuyruk boşalıp yeni görsel gelmeyince durur.
# Konteyner yeniden başlarsa nöbet görevi bunu yeniden başlatır. Kullanım: setsid nohup bash surekli.sh &
A=/mnt/project-files/arastirma/sanat-tarihi/lebriz/araclar
while true; do
  bash $A/calistir.sh > ~/lebriz-tur.txt 2>&1; echo "cikis=$? $(date -u +%FT%H:%M)" >> ~/lebriz-tur.txt
  cat ~/lebriz-tur.txt >> ~/lebriz-turlar.log
  k=$(grep -o 'BITTI indirilen=[0-9]* toplam=[0-9]* kuyruk=[0-9]*' ~/lebriz-tur.txt | tail -1 | grep -o 'kuyruk=[0-9]*' | cut -d= -f2)
  g=$(grep -o 'BITTI gorsel=[0-9]*' ~/lebriz-tur.txt | tail -1 | cut -d= -f2)
  if [ "${k:-1}" = 0 ] && [ "${g:-1}" = 0 ]; then echo "TAMAMLANDI $(date -u +%FT%H:%M)" >> ~/lebriz-turlar.log; break; fi
  if grep -qE '403|429' <(tail -50 /mnt/project-files/arastirma/sanat-tarihi/lebriz/koruma/hatalar.tsv); then echo "ENGEL? durdu $(date -u +%FT%H:%M)" >> ~/lebriz-turlar.log; break; fi
  sleep 60
done
