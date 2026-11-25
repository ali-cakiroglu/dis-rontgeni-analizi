# İddia tablosu (Hafta 1-B)

Hedef dergi: Dentomaxillofacial Radiology · 25 Kasım 2026

## Tek cümlelik katkı

On a leakage-checked external set from other clinics, using other centres' panoramic radiographs only for pre-training gave caries AP50 0.395, versus 0.323 for the single-model baseline (paired difference 0.072, 95% CI 0.016–0.125) and 0.074 when the same images stayed mixed into training.

## İddia tablosu

Form "üç ya da dört satır" istiyor; ana tablo 4 satır:

| # | İddia | Kanıt (sayı ya da şekil) | Şekil/Tablo | Durum |
|---|---|---|---|---|
| 1 | Dış veriyi yalnız ön eğitimde kullanmak, doğrudan karıştırmaktan daha yüksek dış doğrulama çürük AP50'si verir | 0,395 [%95 GA 0,309–0,483] ve 0,074; eşleştirilmiş fark +0,321 [+0,254 – +0,383] (dış doğrulama, 180 röntgen) | Tablo 1 | var |
| 2 | Yöntemin tek modelli baseline'a dış doğrulamadaki üstünlüğü rastlantı değildir; iç testte kayıp yoktur | Eşleştirilmiş önyükleme (aynı röntgenler, 2000 yineleme): dış 0,395 − 0,323 = +0,072 [%95 GA +0,016 – +0,125], p = 0,009; iç test −0,007 [−0,069 – +0,047], fark yok | Tablo 1 | var |
| 3 | Ölçüm bağımsız: sızıntı yok, eşik yalnız doğrulamada seçildi | En küçük Hamming uzaklığı 28/256 (sınır 10); eşik çürük 0,14, kanal tedavisi 0,28; dış çürük 4 alt küme 0,403 ± 0,047 | Tablo 2 | var |
| 4 | Kazanç, dış veriyle yapılan ara aşamadan gelir; yalnız fazladan ince ayardan değil | Kontrol: baseline (best_yolo26s.pt) ara aşama atlanarak aynı ayarlarla (curuk_bizim.yaml, 20 epok, 1024 piksel, batch 4) doğrudan kendi verisiyle ince ayarlanacak (ablasyon) | Tablo 1 | yapılacak |

Yapılacak iddia sayısı: 1 (iddia 4, ablasyon eğitimi). Tıbbi (tanı ya da tedavi) iddia yok.

Sayıların kaynağı: iddia 1–2 ve özet makale_hazirlik/eslesmis_test.py çıktısıdır (eslesmis_test.json; üç model aynı değerlendirme koduyla). Ultralytics doğrulamasının verdiği 0,320 ve 0,070 (kısa rapor, 13 Kasım) bundan yuvarlama düzeyinde farklıdır; makalede yalnız eşleştirilmiş koddaki değerler kullanılacak.

Sonraki haftalar için ek satırlar (tabloya henüz alınmadı):

- Kanal tedavisi dış doğrulamada da yüksek kalır: AP50 iç 0,950 → dış 0,741 [0,651–0,816] (Tablo 2, Şekil 2; var).
- Aynı veride yayımlanmış YOLOv8'e göre kesinlik yüksek, duyarlılık düşük; bu üstünlük değil, ödünleşim: K 0,524 / D 0,375 ve K 0,466 / D 0,439 [2] (Tablo 3; var, karşılaştırılan çalışmanın eşiği bilinmiyor).
- Araç öğrencinin röntgen okumasına geri bildirim sağlar: pilot okuma çalışması, 2 okuyucu, 10 röntgen (Şekil 4; yapılacak).
