# Makale planı · Hafta 1/5 — dergi kartı ve iddia tablosu

25 Kasım 2026 · EEM4011 · Ali Çakıroğlu


## Geçici İngilizce başlık ve özet

**Title (14 words):** Pre-training on external panoramic radiographs and cross-clinic caries detection in an educational support tool

**Abstract:**

Objectives: To examine whether panoramic radiographs from other centres help a caries detector generalise to unseen clinics when they are used only for pre-training instead of being mixed into the training set, within a feedback tool for dental students. Methods: A public dataset of 1,628 annotated panoramic radiographs (CC BY 4.0) and its separate 180-image external validation set from other clinics were used. A YOLO26s caries detector was pre-trained on 5,059 panoramic radiographs from other public sources and then fine-tuned on the training split only; a YOLO26m model trained on 14 classes supplied root canal treatment detections. Confidence thresholds were fixed on the validation split and applied once to the test sets. Near-duplicate leakage was checked with 256-bit image hashes. AP50 was reported with 1000-resample bootstrap 95% confidence intervals and the spread over four fixed subsets. Results: No test or external image was a near-duplicate of a training, validation or pre-training image (minimum Hamming distance 28 of 256 bits). On external validation, caries AP50 was 0.395 (95% CI 0.309–0.483) with pre-training only, 0.320 for a single-model baseline and 0.070 when the external images were mixed directly into training. Root canal treatment reached AP50 0.741 (0.651–0.816) externally and 0.950 internally. Conclusions: Using external radiographs only for pre-training was associated with a higher external caries AP50 than direct mixing; the gain over the baseline lies within the confidence interval and still needs a paired test. The tool is meant as a learning aid for students, not as a diagnostic device.

## Hedef ve yedek dergi

- **Hedef:** Journal of Dentistry (Elsevier, ISSN 0300-5712). Scimago 2025: Q1, Dentistry (miscellaneous) alanında 199 dergi arasında 6. Scopus, Web of Science ve PubMed'de dizinli; yağmacı işareti yok (Science AI Journal herkese açık profili, 25 Kasım 2026).
- **Yedek:** Diagnostics (MDPI, ISSN 2075-4418). Scimago 2025: Q2 (Clinical Biochemistry, 125 dergi arasında 41.). Veri setimizin türetildiği makale bu dergide yayımlandı [2].
- **LaTeX sınıfı:** elsarticle (Elsevier). Kılavuz .tex dosyası kabul ediyor, sınıf adını vermiyor.
- **Yazar kılavuzu:** https://www.sciencedirect.com/journal/journal-of-dentistry/publish/guide-for-authors

## Dergi kartı (Journal of Dentistry yazar kılavuzundan, 25 Kasım 2026)

| Satır | Kılavuzda yazan |
|---|---|
| Makale türü | Original Research Report; ayrıca Digital Dentistry Section: Full Length Article. Case report kabul edilmez. |
| Uzunluk sınırı | En çok 6 basılı sayfa ≈ 20 sayfa metin, şekil ve tablolar dahil. |
| Özet biçimi | En çok 250 kelime; amaç, yöntem, ana bulgular ve sonuç; kaynak ve standart dışı kısaltma yok. Yapılandırılmış başlık zorunluluğu kılavuzda yok. |
| Anahtar kelime | 1–7 adet, İngilizce. |
| Highlights / graphical abstract | İkisi de "encouraged" (zorunlu değil). Highlights 3–5 madde, her biri en çok 85 karakter, ayrı dosya. Graphical abstract en az 1328 piksel genişlik. |
| Hakemlik | Double anonymized; başlık sayfası ile anonim metin ayrı dosya. |
| Zorunlu beyanlar | Çıkar çatışması (declarations tool, .docx), fon kaynağı, insan çalışması etik beyanı, CRediT yazar katkıları, üretken YZ beyanı, veri beyanı (Option B: veriyi depoya koy ya da neden paylaşılamadığını yaz). |
| Kaynak biçimi | Köşeli parantez içinde numara, metindeki sıraya göre; dergi adları LTWA'ya göre kısaltılır; DOI varsa eklenir; veri setinin önüne [dataset]. Kaynak sayısı sınırı kılavuzda yok. |
| Şekil kuralları | Her şekil ayrı dosya; fotoğraf/röntgen TIFF, JPG ya da PNG, en az 300 dpi (tek sütun 1063 piksel); çizgi çizimi en az 1000 dpi; vektör EPS ya da PDF. Hasta görüntüsünü YZ ile üretmek ya da değiştirmek yasak. |
| LaTeX sınıfı | .tex kabul ediliyor, çift sütun yalnız LaTeX'te serbest; sınıf adı (elsarticle) kılavuzda yok. |
| APC / OA | Hibrit: abonelik (ücretsiz) ya da altın açık erişim; APC 3.920 USD (vergiler hariç). |
| YZ politikası (aynen) | "Authors preparing a manuscript for this journal may use AI tools to support them. However, these tools must never be used as a substitute for human critical thinking, expertise, and evaluation. AI tools may only be applied with human oversight and control." Beyan, kaynakçadan önce şu başlıkla yazılır: "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process." YZ araçları yazar olarak gösterilemez. |

### Makaleye beş sonucu

1. Metin şekil ve tablolarla birlikte yaklaşık 20 sayfada kalmalı; Tablo 1 ve Tablo 2 birleştirilebilir, ayrıntılar ek dosyaya taşınır.
2. Hakemlik çift kör: başlık sayfası ayrı dosya olur; metinde yazar adı, kurum ve GitHub linki bulunmaz.
3. Hasta görüntüsü olan şekiller (örnek röntgenler) en az 300 dpi olmalı ve YZ ile değiştirilmemeli; yalnız model çıktısı kutuları eklenebilir.
4. Kaynaklar köşeli parantezli numara biçiminde olmalı ve her birinde DOI bulunmalı; veri setleri [dataset] etiketiyle verilir.
5. Kaynakçadan önce üretken YZ beyanı bölümü eklenir; veri beyanında veri setinin Zenodo DOI'si verilir; röntgen görüntüleri anonim olduğu için hasta onamı gerekmediği belirtilir.

## Dergide son iki yıldaki benzer üç makale (Crossref'te doğrulandı)

1. Gracea et al. Two-stage deep learning approach for impacted canine automated detection and segmentation on panoramic radiographs. J Dent. 2026. https://doi.org/10.1016/j.jdent.2026.106463
2. Bourtzinakou et al. An AI agent-based system for interpretable panoramic dental X-ray analysis. J Dent. 2026. https://doi.org/10.1016/j.jdent.2026.106368
3. Fidler et al. Effect of lossy JPEG compression on AI diagnostic output stability in panoramic radiograph analysis. J Dent. 2027. https://doi.org/10.1016/j.jdent.2026.107033

Not: Bu üç makale henüz indirilip okunmadı; katkı düzeyi karşılaştırması yapılacak.

## Tek cümlelik katkı

On a leakage-checked external set from other clinics, using other centres' panoramic radiographs only for pre-training gave caries AP50 0.395, versus 0.070 when the same images were mixed directly into training.

## İddia tablosu

Form "üç ya da dört satır" istiyor; ana tablo 4 satır:

| # | İddia | Kanıt (sayı ya da şekil) | Şekil/Tablo | Durum |
|---|---|---|---|---|
| 1 | Dış veriyi yalnız ön eğitimde kullanmak, doğrudan karıştırmaktan daha yüksek dış doğrulama çürük AP50'si verir | 0,395 [%95 GA 0,309–0,483] ve 0,070 (dış doğrulama, 180 röntgen) | Tablo 1 | var |
| 2 | Yöntemin tek modelli baseline'a üstünlüğü (0,395 ve 0,320) rastlantı değildir | Fark için eşleştirilmiş önyükleme; şu an 0,320 yöntemin %95 GA'sı içinde | Tablo 1 | yapılacak |
| 3 | Ölçüm bağımsız: sızıntı yok, eşik yalnız doğrulamada seçildi | En küçük Hamming uzaklığı 28/256 (sınır 10); eşik çürük 0,14, kanal tedavisi 0,28; dış çürük 4 alt küme 0,403 ± 0,047 | Tablo 2 | var |
| 4 | Kazanç model boyutundan değil ön eğitimden gelir | Aynı YOLO26s, aynı ayarlarla ön eğitimsiz eğitilecek (ablasyon) | Tablo 1 | yapılacak |

Yapılacak iddia sayısı: 2. Tıbbi (tanı ya da tedavi) iddia yok.

Sonraki haftalar için ek satırlar (tabloya henüz alınmadı):

- Kanal tedavisi dış doğrulamada da yüksek kalır: AP50 iç 0,950 → dış 0,741 [0,651–0,816] (Tablo 2, Şekil 2; var).
- Aynı veride yayımlanmış YOLOv8'e göre kesinlik yüksek, duyarlılık düşük; bu üstünlük değil, ödünleşim: K 0,524 / D 0,375 ve K 0,466 / D 0,439 [2] (Tablo 3; var, karşılaştırılan çalışmanın eşiği bilinmiyor).
- Araç öğrencinin röntgen okumasına geri bildirim sağlar: pilot okuma çalışması, 2 okuyucu, 10 röntgen (Şekil 4; yapılacak).
