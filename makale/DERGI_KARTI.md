# Makale planı · Hafta 1/5 — dergi kartı ve iddia tablosu

25 Kasım 2026 · EEM4011 · Ali Çakıroğlu


## Dergi araması (Pre-Check & Journal Finder, 25 Kasım 2026)

- Ali'nin hesabıyla çalıştırıldı. Alan: Computer Science. Kabul olasılığı tahmini: üst düzey %5, orta düzey (alan Q1/Q2) %59, açık/yeni dergiler %69. Önceki yayın kontrolü: eşleşme yok (kısmi kontrol).
- Önerilen ilk dergiler: Dentomaxillofacial Radiology %82 (A), Diagnostics %28 (C), BMC Oral Health %14 (D), Journal of Imaging %10 (D). Journal of Dentistry ilk 10'da yok.
- Uyarı: özette motivasyon ve sonuç eksik görünüyor → aşağıdaki özet buna göre yeniden yazıldı.
- Karar: hedef Journal of Dentistry'den **Dentomaxillofacial Radiology**'ye çevrildi (kapsamı doğrudan dental radyoloji; Journal of Dentistry kılavuzu ana alanını "Restorative Dentistry" olarak tanımlıyor).

## Geçici İngilizce başlık ve özet (DMFR biçimi: yapılandırılmış, en çok 250 kelime, kısaltma ve atıf yok)

**Title (14 words):** Pre-training on external panoramic radiographs and cross-clinic caries detection in an educational support tool

**Abstract:**

Objectives: Caries detectors trained on panoramic radiographs from one centre lose accuracy in other clinics, limiting their use as student feedback tools. This study examined whether radiographs from other centres help when they are used only for pre-training rather than mixed into the training set. Methods: A public dataset of 1628 annotated panoramic radiographs and its separate external validation set of 180 radiographs from other clinics were used. A one-stage object detector for caries was pre-trained on 5059 panoramic radiographs from other public sources and then fine-tuned on the training split only; a second detector trained on 14 classes supplied root canal treatment detections. Confidence thresholds were fixed on the validation split. Near-duplicates were checked with 256-bit image hashes. Average precision at 50% box overlap was reported with 1000-resample bootstrap 95% confidence intervals. Results: No test or external image was a near-duplicate of a training image. On external validation, caries average precision was 0.395 (95% confidence interval 0.309–0.483) with pre-training only, 0.320 for a single-model baseline and 0.070 when the external images were mixed directly into training. Root canal treatment reached 0.741 (0.651–0.816) externally and 0.950 internally. Conclusions: Using external radiographs only for pre-training was associated with higher external caries average precision than direct mixing; the gain over the baseline lies within the confidence interval and requires a paired test. Advances in knowledge: The study separates how multi-centre radiographs enter training from the radiographs themselves, under leakage-checked external validation, in a feedback tool for dental students.

## Hedef ve yedek dergi

- **Hedef:** Dentomaxillofacial Radiology (DMFR; Oxford University Press, British Institute of Radiology adına; ISSN 0250-832X). Scimago 2025: dört alanın dördünde Q1 (Otorhinolaryngology 128 içinde 4., Dentistry 199 içinde 12., Radiology 360 içinde 49.). Scopus, Web of Science, PubMed; yağmacı işareti yok. Journal Finder'da en iyi eşleşme (%82).
- **Yedek:** Diagnostics (MDPI, ISSN 2075-4418). Scimago 2025: Q2. Journal Finder'da 2. sıra; veri setimizin makalesi bu dergide yayımlandı [2].
- **LaTeX sınıfı:** Diğer. Kılavuz Oxford'un RASTI sınıfını öneriyor, başka sınıfları da kabul ediyor; Overleaf'te şimdilik hocanın elsarticle iskeleti.
- **Yazar kılavuzu:** https://academic.oup.com/dmfr/pages/general-instructions

## Dergi kartı (DMFR "Instructions to Authors", 25 Kasım 2026)

| Satır | Kılavuzda yazan |
|---|---|
| Makale türü | Research Article ("novel original research in a clear, reproducible way"); Technical Report ve Short Communication da var. Case report kabul edilmez. |
| Uzunluk sınırı | Research Article: en çok 7.000 kelime, en çok 50 kaynak, en çok 10 şekil ve 5 tablo. Introduction, Methods, Results, Discussion başlıkları zorunlu. |
| Özet biçimi | En çok 250 kelime; atıf ve kısaltma yok; yapılandırılmış: Objectives, Methods, Results, Conclusions ve "Advances in knowledge" (1–2 cümle: çalışmanın neden yeni olduğu ve ne kattığı). Özet başlık sayfasında da yer alır. |
| Anahtar kelime | En az 3, en çok 10. |
| Highlights / graphical abstract | Kılavuzda yok (yerine özette "Advances in knowledge"). |
| Hakemlik | Double-anonymised; genellikle 2 hakem; yazar hakem önerebilir. |
| Zorunlu beyanlar | Çıkar çatışması (başlık sayfası), fon kaynağı (başlık sayfasında ayrı alt başlık, hibe numarasıyla), etik onay ya da onay gerekmediği (Methods'ta, kurulun adıyla), CRediT yazar katkıları, gönderen yazar için ORCID. Veri ve kod paylaşımı "strongly encourages" (zorunlu değil). Raporlama: tanısal doğruluk çalışmasında STARD. |
| Kaynak biçimi | Vancouver: metinde Arap rakamı, atıf sırasına göre; dergi adları MEDLINE kısaltması; altıdan fazla yazarda "et al". Genel stil AMA, İngiliz yazımı. |
| Şekil kuralları | jpeg/jpg/png/tiff/svg/pdf/eps; renkli 300 dpi, gri tonlu 600 dpi, karma 600–900 dpi, çizgi 1200 dpi; grafik ve diyagram vektör tercih edilir; her şekle "Alt text:" zorunlu; hasta kimliği görüntüden silinir; renk ücreti yok. |
| LaTeX sınıfı | Overleaf'teki RASTI sınıfı önerilir; "papers prepared using other class files can also be accepted". |
| APC / OA | Standart lisans ücretsiz; CC BY ya da CC BY-NC açık erişim 2.392 £; BIR üyelerine %20 indirim; sayfa ve renk ücreti yok. |
| YZ politikası (aynen) | "Natural language processing tools driven by artificial intelligence (AI) do not qualify as authors, and the Journal will screen for them in author lists. The use of AI (for example, to help generate content, write code, or process data) should be disclosed both in cover letters to editors and in the Methods or Acknowledgements section of manuscripts. Please see the COPE position statement on Authorship and AI for more details." Şekiller için ayrı YZ kuralı kılavuzda yok; görüntü üzerinde uygunsuz değişiklik taraması yapıldığı yazıyor. |

### Makaleye beş sonucu

1. Özet beş alt başlıklı olmalı ve kısaltma içermemeli: AP50, CI, YOLO gibi kısaltmalar özette açık yazılır; "Advances in knowledge" cümlesi katkı cümlesinden türetilir.
2. Metin en çok 7.000 kelime, 50 kaynak, 10 şekil ve 5 tablo; hocanın 25–40 kaynak hedefi bu sınırın içinde kalıyor.
3. Çift kör hakemlik: ad, kurum, teşekkür, fon ve GitHub linki yalnız başlık sayfasında; ana metinde yazar izi kalmaz.
4. Yapay zekâ kullanımı (metin taslağı, kod) hem kapak mektubunda hem Methods ya da Acknowledgements'ta beyan edilir; şekillerdeki her röntgene "Alt text" yazılır ve hasta bilgisi görünmez.
5. Etik cümlesi Methods'a girer: açık ve kimliksizleştirilmiş veri kullanıldığı için etik onay gerekmediği yazılır; tanısal doğruluk çalışmasına yakın olduğu için STARD maddeleri kontrol edilir.

## Dergide son iki yıldaki benzer üç makale (Crossref'te doğrulandı)

1. Lee et al. Cross-vendor robustness of a hybrid deep learning framework for 4-stage periodontitis classification on panoramic radiographs. Dentomaxillofac Radiol. 2026. https://doi.org/10.1093/dmfr/twag055
2. Farooqi et al. External validation of 2 artificial intelligence systems for dentinal caries detection: a retrospective pilot clinical outcomes study. Dentomaxillofac Radiol. 2026. https://doi.org/10.1093/dmfr/twag054
3. Rubak et al. Impact of labelling inaccuracy and image noise on tooth segmentation in panoramic radiographs using federated, centralized, and local learning. Dentomaxillofac Radiol. 2026. https://doi.org/10.1093/dmfr/twag001

Not: Bu üç makale henüz indirilip okunmadı; katkı düzeyi karşılaştırması yapılacak.

Önceki hedef (Journal of Dentistry) için bulunan makaleler: 10.1016/j.jdent.2026.106463, 10.1016/j.jdent.2026.106368, 10.1016/j.jdent.2026.107033.

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
