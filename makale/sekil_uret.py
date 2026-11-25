"""sonuclar.csv -> sekiller/Figure_2.pdf   (Şekil 1 iskeletteki blok diyagramdır; dosya numarası PDF'teki şekil numarasıdır)
Çalıştırma: python3 sekil_uret.py   (Windows'ta: python sekil_uret.py). Bilgisayarınızda matplotlib kurulu olmalıdır:
komut satırına bir kez  pip install matplotlib  yazınız (yoksa betik ModuleNotFoundError verir).
Dergi ölçüsü: tek sütun genişliği (88 mm), 8 pt yazı, vektör PDF, gömülü yazı tipi, başlık şekil içinde YOK.
KENDİ DOSYANIZ İÇİN (HAFTA 3-B, 4-A): bu betik de örnek sütun adlarını okur; sonuc_uret.py ile aynı biçimde uyarlatınız.
MATLAB'da: exportgraphics(gcf,'sekiller/Figure_2.pdf','ContentType','vector'), 88 mm genişlik, 8 pt yazı.
Şekli bu betik çizer; şekil ya da görüntü yapay zekâya ürettirilmez (sohbet yalnız bu kodu düzeltebilir; düzelttirdiyseniz
beyan edilir: Elsevier'de veri grafiği için Methods'ta aracın adı, sürümü ve geliştiricisi; IEEE'de Acknowledgment; HAFTA 5-A).
Metriğinizde düşük değer iyiyse eksen adını ve 'Proposed' etiketlerini buna göre yazınız (ör. 'MAE (bpm)')."""
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 8, 'font.family': 'serif', 'pdf.fonttype': 42, 'axes.linewidth': 0.6})
kat = list(csv.DictReader(open('sonuclar.csv', encoding='utf-8-sig')))
b = [float(r['baseline']) for r in kat]
y = [float(r['onerilen']) for r in kat]

fig, ax = plt.subplots(figsize=(88 / 25.4, 62 / 25.4))     # mm -> inç
for bi, yi in zip(b, y):                                   # her kat için eşleştirilmiş çift (ince gri çizgi)
    ax.plot([0, 1], [bi, yi], color='0.75', lw=0.6, zorder=1)
ax.scatter([0] * len(b), b, s=16, marker='o', color='#2a78d6', zorder=2, label='Baseline')
ax.scatter([1] * len(y), y, s=16, marker='s', color='#eb6834', zorder=2, label='Proposed')
for x, v in ((0, b), (1, y)):                              # ortalama: kalın yatay çizgi
    m = sum(v) / len(v)
    ax.plot([x - 0.14, x + 0.14], [m, m], color='0.1', lw=1.6, zorder=3)
ax.set_xlim(-0.5, 1.5)
ax.set_xticks([0, 1], ['Baseline', 'Proposed'])
ax.set_ylabel('Balanced accuracy (unitless)')              # eksen adı + birim her zaman yazılır
ax.spines[['top', 'right']].set_visible(False)
ax.grid(axis='y', lw=0.3, color='0.88')
ax.set_axisbelow(True)
fig.tight_layout(pad=0.4)
fig.savefig('sekiller/Figure_2.pdf')
print('sekiller/Figure_2.pdf: tamam')
