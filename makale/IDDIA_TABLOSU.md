# İddia tablosu (Hafta 1-B)

Hedef dergi: Dentomaxillofacial Radiology · 25 Kasım 2026

## Tek cümlelik katkı

On a leakage-checked external set from other clinics, using other centres' panoramic radiographs only for pre-training gave caries AP50 0.395, versus 0.070 when the same images were mixed directly into training.

## İddia tablosu

Form "üç ya da dört satır" istiyor; ana tablo 4 satır:

| # | İddia | Kanıt (sayı ya da şekil) | Şekil/Tablo | Durum |
|---|---|---|---|---|
| 1 | Dış veriyi yalnız ön eğitimde kullanmak, doğrudan karıştırmaktan daha yüksek dış doğrulama çürük AP50'si verir | 0,395 [%95 GA 0,309–0,483] ve 0,070 (dış doğrulama, 180 röntgen) | Tablo 1 | var |
| 2 | Yöntemin tek modelli baseline'a üstünlüğü (0,395 ve 0,320) rastlantı değildir | Fark için eşleştirilmiş önyükleme; şu an 0,320 yöntemin %95 GA'sı içinde | Tablo 1 | yapılacak |
| 3 | Ölçüm bağımsız: sızıntı yok, eşik yalnız doğrulamada seçildi | En küçük Hamming uzaklığı 28/256 (sınır 10); eşik çürük 0,14, kanal tedavisi 0,28; dış çürük 4 alt küme 0,403 ± 0,047 | Tablo 2 | var |
| 4 | Kazanç model boyutundan değil ön eğitimden gelir | Aynı YOLO26s aynı ayarlarla ön eğitimsiz eğitilecek (ablasyon) | Tablo 1 | yapılacak |

Yapılacak iddia sayısı: 2. Tıbbi (tanı ya da tedavi) iddia yok.

Sonraki haftalar için ek satırlar (tabloya henüz alınmadı):

- Kanal tedavisi dış doğrulamada da yüksek kalır: AP50 iç 0,950 → dış 0,741 [0,651–0,816] (Tablo 2, Şekil 2; var).
- Aynı veride yayımlanmış YOLOv8'e göre kesinlik yüksek, duyarlılık düşük; bu üstünlük değil, ödünleşim: K 0,524 / D 0,375 ve K 0,466 / D 0,439 [2] (Tablo 3; var, karşılaştırılan çalışmanın eşiği bilinmiyor).
- Araç öğrencinin röntgen okumasına geri bildirim sağlar: pilot okuma çalışması, 2 okuyucu, 10 röntgen (Şekil 4; yapılacak).
