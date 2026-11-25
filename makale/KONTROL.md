# KONTROL — her teslimden önce (5 dakika); tamamı HAFTA 5-B'de

Bu listeyi her hafta formu göndermeden önce o haftanın satırlarıyla, 5. haftada baştan sona uygulayınız. "Hayır" çıkan satırı düzeltmeden göndermeyiniz. Köşeli parantez içindeki hafta, satırın ilk kez geçerli olduğu haftadır.

## Derleme
- [ ] [1] Overleaf'te Recompile: kırmızı hata sayısı 0; derleyici pdfLaTeX.
- [ ] [1] PDF'te `??` araması: 0 sonuç (`??` = eksik sonuç makrosu ya da kırık atıf/etiket).
- [ ] [2] Günlükte (Logs) "Reference … undefined" ya da "Citation … undefined" uyarısı yok ("Font shape … undefined" zararsızdır). "empty pages in …" uyarısı varsa eksik alanı kaynağın kendi PDF'inden tamamlayınız (uydurmayınız).
- [ ] [5] 1. sayfadaki ÖRNEK İSKELET kutusu silindi (`govde.tex` başındaki `\ornekuyarisi` satırı).

## Sayılar
- [ ] [3] Özet, Results, Discussion ve Conclusion'daki her sonuç sayısı `\sonuc{...}` ile yazıldı; "her katta" gibi sayımlar da makrodan (`fark.npos`).
- [ ] [2] `veri_ozeti.csv` kendi veri setimin sayılarını içeriyor (örnekteki 400 / 100 / 2000 değil); betik çalıştırıldı ve PDF'te kendi sayılarım görünüyor.
- [ ] [3] Metriğimde düşük değer iyiyse `IYI_YON = -1`; metindeki 'rose', 'higher', 'improved' kelimeleri sonucumun yönüyle uyumlu.
- [ ] [3] `sonuclar.csv` değiştiyse `python3 sonuc_uret.py` ve `python3 sekil_uret.py` yeniden çalıştırıldı (Windows'ta: `python sonuc_uret.py`); betikler metriğime uyarlandı; `sonuclar.tex` elle doldurulmadı.
- [ ] [3] Her istatistiğin yanında n (kayıt, kişi ya da kat sayısı) yazıyor; metrik görev türüne uygun ve birimi yazılı.
- [ ] [3] Baseline ve yeniden koşulan yayımlanmış yöntem aynı veride ve aynı bölmede; başka makalelerden alınan sayılar ayrı tabloda ve "doğrudan karşılaştırılamaz" notuyla.

## Şekil ve tablo
- [ ] [4] Her şekil ve tablo metinde `\ref` ile anılıyor; dosya adları PDF'teki numaralarla aynı (Figure_2.pdf = Şekil 2).
- [ ] [4] Şekil ve görüntülerin hiçbiri yapay zekâya ürettirilmedi ya da değiştirtilmedi; çizim kodu düzelttirildiyse beyanda ve (Elsevier) o şeklin altyazısında ya da Methods'ta araç adı ve sürümüyle yazıyor.
- [ ] [4] Şekiller vektör PDF, basılı genişlikte (tek sütun ~88 mm), yazılar ~8 pt; eksen adı ve birimi var; şekil içinde başlık yok.
- [ ] [4] Altyazı tek başına anlaşılıyor; tablolar booktabs ile, dikey çizgi yok, birim sütun başlığında.

## Kaynakça
- [ ] [2] `refs.bib` içinde 2. haftada en az 20, 4. haftadan sonra 25–40 kaynak var; her biri açılıp okundu, DOI'si var ve metinde anılıyor (DOI'siz veri sayfası: `@misc` + url + erişim tarihi).
- [ ] [2] Kaynakların yarıdan fazlası son beş yıldan; en az üçü HEDEF derginin son üç yılından ve metinde tartışılıyor (veri seti ve yazılım atıfları sayılmaz).
- [ ] [2] Ders raporu ya da 2209-A başvurusu gibi yayımlanmamış metin kaynak olarak gösterilmedi.

## Dergi ve beyanlar
- [ ] [5] Özet derginin kelime sınırının altında (Overleaf: Menu → Word Count; PDF'ten de sayınız).
- [ ] [5] Sayfa/kelime sınırı derginin son düzeninde denendi (main.tex başındaki not).
- [ ] [5] Beyan başlıkları kılavuzdaki adlarla ve sırayla; her beyan DOĞRU (etik, veri, kod, katkı, çıkar çatışması, destek).
- [ ] [5] Yapay zekâ beyanı sohbete yaptırılan her işi ve bölümü sayıyor; kod yardımı Methods'ta anılıyor; kullanım derginin politikasına uyuyor.
- [ ] [5] Veri lisansı ve sürümü yazılı; ham veri ve kimlik taşıyan bilgi depoda ve makalede yok.
- [ ] [5] (Elsevier) highlights.txt: 3–5 madde, her biri en çok 85 karakter, sonuç sayısı yok.
- [ ] [5] Kapak mektubu yazıldı (beş cümle) ve GitHub'da `makale/KAPAK_MEKTUBU.md` dosyasında.
- [ ] [5] Dergiye kaynak dosya yüklenecekse bütün dosyalar tek klasöre (köke) alındı; `\graphicspath` sayesinde şekiller yine bulunur.

## Dürüstlük
- [ ] [1] Yapılmamış bir deney, eklenmemiş bir şekil ya da okunmamış bir kaynak metinde "yapıldı" gibi geçmiyor.
- [ ] [1] Yapay zekâ çıktısı olduğu gibi yapıştırılmadı; [KONTROL] işaretli her cümle doğrulandı.
- [ ] [4] Discussion ve Conclusion'daki yorumlar benim notlarımdan.
- [ ] [5] Deneme hakemliğine main.tex değil, Overleaf'ten indirilen derlenmiş PDF yüklendi.
