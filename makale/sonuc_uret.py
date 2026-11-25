r"""sonuclar.csv + veri_ozeti.csv  ->  sonuclar.tex
Çalıştırma: python3 sonuc_uret.py   (Windows'ta: python sonuc_uret.py). İki CSV bu betikle AYNI klasörde olmalıdır.
Makaledeki HER sonuç sayısı bu dosyanın ürettiği makrolardan gelir; metne elle sayı yazılmaz.
KENDİ DOSYANIZ İÇİN (HAFTA 3-B): bu betik örnek sütunları (baseline, onerilen, isteğe bağlı yayin) okur; satır sayısı kat.n olur.
Sohbetinize sonuclar.csv dosyanızın başlık satırını ve ilk üç satırını, görev türünüzü ve metriğinizi ve bu betiği veriniz;
betiği sütun adlarınıza VE metriğinize uyarlatınız (ör. kestirimde ortalama fark ve %95 uyum sınırları, olay tespitinde
toplam TP, FN, FP'den Se ve +P, bölütlemede Dice medyanı). Her yeni hesap betiğe satır olarak eklenir; sayıyı sohbet yazmaz.
METRİĞİNİZİN YÖNÜ: aşağıdaki IYI_YON satırı. Yüksek değer iyiyse (doğruluk, Dice) 1, düşük değer iyiyse (MAE, RMSE, hata oranı) -1.
fark.npos, yöntemin DAHA İYİ olduğu satır sayısıdır; fark.ort ise her zaman 'önerilen - baseline' farkıdır (düşük-iyi metrikte iyileşme
eksi çıkar). Metindeki 'rose', 'higher', 'improved' gibi yön bildiren kelimeleri kendi sonucunuza göre seçiniz.
veri_ozeti.csv: örnek değerleri (400, 100, 2000) kendi verinizinkiyle değiştiriniz (HAFTA 2-B). Çalıştırdıktan sonra sonuclar.tex
dosyasını Overleaf'e yükleyip veri.kayit, veri.kisi, veri.fs değerlerinin sizin verinize ait olduğunu kontrol ediniz; Overleaf betik çalıştırmaz.
CSV'yi Excel'de kaydettiyseniz ayırıcı virgül, ondalık işareti nokta olmalıdır (Türkçe Excel noktalı virgül kullanır; betik KeyError verir).
Bu betik ek kurulum istemez (yalnız Python). Betik çalışmıyorsa hata mesajını sohbetinize yapıştırınız."""
import csv, itertools, random, statistics as st

IYI_YON = 1   # metriğinizde YÜKSEK değer iyiyse 1 (doğruluk, Dice); DÜŞÜK değer iyiyse -1 (MAE, RMSE, hata oranı)

satir = list(csv.DictReader(open('sonuclar.csv', encoding='utf-8-sig')))
b = [float(r['baseline']) for r in satir]          # her satır (kat ya da test kişisi) için baseline değeri
y = [float(r['onerilen']) for r in satir]          # aynı satırda önerilen yöntemin değeri


def f3(v):
    """Üç ondalık; eksi işareti LaTeX'te doğru basılsın diye \\ensuremath{-} olarak yazılır."""
    s = f'{v:.3f}'
    return '0.000' if float(s) == 0 else s.replace('-', '\\ensuremath{-}')


def eslestirilmis(d):
    """Eşleştirilmiş farklar -> ortalama, %95 bootstrap güven aralığı, işaret değiştirme (permütasyon) testi."""
    n, ort = len(d), st.mean(d)
    random.seed(2026)                              # tohum sabit: herkes aynı aralığı ve aynı p değerini bulur
    bs = sorted(st.mean(random.choices(d, k=n)) for _ in range(10000))
    alt, ust = bs[249], bs[9749]                   # farkın %95 bootstrap güven aralığı
    if n <= 16:                                    # tam (exact) test: 2**n işaret düzeninin hepsi denenir
        asiri = sum(abs(sum(s * x for s, x in zip(isr, d)) / n) >= abs(ort) - 1e-12
                    for isr in itertools.product((1, -1), repeat=n))
        p, test = asiri / 2 ** n, 'exact'
    else:                                          # 2**n çok büyük: 100 000 rastgele işaret düzeni (tohum sabit)
        B = 100000
        asiri = sum(abs(sum(s * x for s, x in zip(random.choices((1, -1), k=n), d)) / n) >= abs(ort) - 1e-12
                    for _ in range(B))
        p, test = (asiri + 1) / (B + 1), 'Monte Carlo, 100\\,000 sign flips'
    return {'ort': f3(ort), 'alt': f3(alt), 'ust': f3(ust),
            'p': f'= {p:.3f}' if p >= 0.001 else '< 0.001', 'ptest': test,
            'npos': sum(1 for x in d if IYI_YON * x > 0)}   # yöntemin DAHA İYİ olduğu satır sayısı ("her katta" elle yazılmaz)


S = {'kat.n': len(satir), 'base.ort': f3(st.mean(b)), 'base.ss': f3(st.stdev(b)),
     'yeni.ort': f3(st.mean(y)), 'yeni.ss': f3(st.stdev(y))}
S.update({'fark.' + k: v for k, v in eslestirilmis([yi - bi for yi, bi in zip(y, b)]).items()})
if 'yayin' in satir[0]:                            # isteğe bağlı sütun: AYNI satırlarda yeniden koşulan yayımlanmış yöntem
    g = [float(r['yayin']) for r in satir]
    S.update({'yayin.ort': f3(st.mean(g)), 'yayin.ss': f3(st.stdev(g))})
    S.update({'yfark.' + k: v for k, v in eslestirilmis([yi - gi for yi, gi in zip(y, g)]).items()})
S.update({r['anahtar']: r['deger'] for r in csv.DictReader(open('veri_ozeti.csv', encoding='utf-8-sig'))})
with open('sonuclar.tex', 'w', encoding='utf-8') as f:
    f.write('% OTOMATİK ÜRETİLDİ (sonuc_uret.py) -- elle değiştirmeyiniz; sonuclar.csv değişince yeniden üretiniz.\n')
    f.writelines(f'\\sonucyaz{{{k}}}{{{v}}}\n' for k, v in S.items())
print('sonuclar.tex:', len(S), 'makro')
