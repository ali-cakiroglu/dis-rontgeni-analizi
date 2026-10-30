"""2242 raporunun şekillerini üretir (sekiller/ klasörüne).

Şekil 1: sistemin akışı
Şekil 2: iç test ve dış doğrulamada sınıf bazında mAP50 (ölçüm dosyalarından okunur)
Şekil 3: test setinden bir röntgende modelin çıktısı
         (veri setinin görüntüsünü içerir; yalnız raporda kullanılır, açık depoya konmaz)

Kullanım:
    python sekiller.py
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CIKTI = Path(__file__).resolve().parent / "sekiller"
CIKTI.mkdir(exist_ok=True)

YUZEY, MUREKKEP, IKINCIL, IZGARA = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9"
MAVI, TURUNCU = "#2a78d6", "#eb6834"          # kategorik 1. ve 2. renk (doğrulandı)
ATIF = ("Veri: Mureșanu, Hedeșiu, Iacob, Zenodo, DOI: 10.5281/zenodo.15487430, "
        "CC BY 4.0.")

plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": MUREKKEP,
                     "axes.labelcolor": IKINCIL, "xtick.color": IKINCIL,
                     "ytick.color": IKINCIL})


def v(x, b=3):
    return f"{x:.{b}f}".replace(".", ",")


# --------------------------------------------------------------------------- #
# Şekil 1 — akış
# --------------------------------------------------------------------------- #

def kutu(ax, x, y, w, h, metin, kenar=IKINCIL, dolgu="#ffffff", kalin=False, boyut=10):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.4,rounding_size=1.2",
                                linewidth=1.6, edgecolor=kenar, facecolor=dolgu))
    ax.text(x, y, metin, ha="center", va="center", fontsize=boyut,
            fontweight="bold" if kalin else "normal", color=MUREKKEP, linespacing=1.35)


def ok(ax, a, b, kesik=False, renk=IKINCIL):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=14, linewidth=1.5,
                                 color=renk, linestyle=(0, (4, 3)) if kesik else "-"))


def sekil1():
    fig, ax = plt.subplots(figsize=(14, 8.6))
    fig.patch.set_facecolor(YUZEY)
    ax.set_facecolor(YUZEY)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(30, 98.5, "Kullanım (her röntgen için)", ha="center", fontsize=12,
            fontweight="bold", color=IKINCIL)
    ax.text(81, 98.5, "Eğitim (bir kez, çevrim dışı)", ha="center", fontsize=12,
            fontweight="bold", color=IKINCIL)
    ax.plot([61.5, 61.5], [3, 97], color=IZGARA, linewidth=1.5)

    # kullanım akışı
    kutu(ax, 30, 91, 36, 6, "Panoramik röntgen yüklenir", kalin=True)
    kutu(ax, 30, 80, 36, 7, "Ön işleme\n1024 piksel, en-boy oranı korunur")
    kutu(ax, 15, 64, 25, 12, "Ana model — YOLO26m\n14 sınıf\nkanal tedavisi + 11 bulgu",
         kenar=MAVI, dolgu="#eef4fc", kalin=False)
    kutu(ax, 45, 64, 25, 12, "Çürük modeli — YOLO26s\niki aşamalı eğitim\nçürük, periapikal lezyon",
         kenar=TURUNCU, dolgu="#fdf0ea")
    kutu(ax, 30, 47.5, 38, 7, "Birleştirme\nher bulgu, en iyi ölçülen modelden okunur")
    kutu(ax, 30, 35.5, 40, 7, "Hassasiyet seçimi\nTarama 0,10  ·  Dengeli 0,25  ·  Kesin 0,40")
    kutu(ax, 30, 23.5, 46, 7, "Arayüz\nelips + güven skoru  ·  yakın görüntü  ·  ölçülmüş başarı paneli")
    kutu(ax, 30, 10.5, 46, 8, "Öğrenci kendi okumasını karşılaştırır\neğitim amaçlı yardımcı araç — tanı koymaz",
         kalin=True, dolgu="#f3f2ee")

    ok(ax, (30, 87.6), (30, 84))
    ok(ax, (24, 76.3), (16, 70.6))
    ok(ax, (36, 76.3), (44, 70.6))
    ok(ax, (16, 57.4), (24, 51.4))
    ok(ax, (44, 57.4), (36, 51.4))
    ok(ax, (30, 43.6), (30, 39.4))
    ok(ax, (30, 31.6), (30, 27.4))
    ok(ax, (30, 19.6), (30, 15))

    # eğitim paneli
    kutu(ax, 81, 84, 34, 11, "Veri (CC BY 4.0, kimliksizleştirilmiş)\n"
         "eğitim 1.375  ·  doğrulama 153  ·  test 100\n+ 180 dış doğrulama (başka klinikler)",
         boyut=9.5)
    kutu(ax, 81, 67, 34, 8, "Ana model eğitimi\nCOCO ağırlıklarından transfer öğrenme, 40 epok",
         kenar=MAVI, dolgu="#eef4fc", boyut=9.5)
    kutu(ax, 81, 50, 34, 12, "Çürük modeli eğitimi\n1) ön eğitim: kendi verisi\n"
         "    + 5.059 dış kaynaklı röntgen\n2) ince ayar: yalnız kendi verisi",
         kenar=TURUNCU, dolgu="#fdf0ea", boyut=9.5)
    kutu(ax, 81, 31, 34, 11, "Ölçüm\niç test + dış doğrulama\nmAP50, kesinlik, duyarlılık, eşik taraması",
         boyut=9.5)

    ok(ax, (81, 78.2), (81, 71.4))
    ok(ax, (81, 62.6), (81, 56.4))
    ok(ax, (81, 43.6), (81, 36.9))
    ok(ax, (63.6, 58.6), (58, 60.5), kesik=True)
    ax.text(60.6, 55.2, "eğitilmiş\nağırlıklar\n(iki model)", ha="center", va="top",
            fontsize=8.5, color=IKINCIL)

    fig.text(0.5, 0.012, ATIF, ha="center", fontsize=8.5, color=IKINCIL)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    yol = CIKTI / "sekil1_akis.png"
    fig.savefig(yol, dpi=170, facecolor=YUZEY)
    plt.close(fig)
    return yol


# --------------------------------------------------------------------------- #
# Şekil 2 — mAP50
# --------------------------------------------------------------------------- #

def sekil2():
    ana = json.loads((config.WEIGHTS_DIR / "metrics.json").read_text(encoding="utf-8"))["splits"]
    cur = json.loads((config.WEIGHTS_DIR / "curuk2_metrics.json").read_text(encoding="utf-8"))["splits"]
    bulgular = [("Kanal tedavisi", ana, "END"), ("Çürük", cur, "CAR"),
                ("Periapikal lezyon", cur, "API")]
    ic = [k["test"]["classes"][c]["map50"] for _, k, c in bulgular]
    dis = [k["external"]["classes"][c]["map50"] for _, k, c in bulgular]

    fig, ax = plt.subplots(figsize=(9, 5.4))
    fig.patch.set_facecolor(YUZEY)
    ax.set_facecolor(YUZEY)
    x = range(len(bulgular))
    gen = 0.36
    b1 = ax.bar([i - gen / 2 - 0.006 for i in x], ic, gen, color=MAVI, label="İç test (100 röntgen)",
                edgecolor=YUZEY, linewidth=1.5, zorder=3)
    b2 = ax.bar([i + gen / 2 + 0.006 for i in x], dis, gen, color=TURUNCU,
                label="Dış doğrulama (180 röntgen, başka klinikler)", edgecolor=YUZEY,
                linewidth=1.5, zorder=3)
    for cubuk, deger in list(zip(b1, ic)) + list(zip(b2, dis)):
        ax.text(cubuk.get_x() + cubuk.get_width() / 2, deger + 0.015, v(deger),
                ha="center", va="bottom", fontsize=10, color=MUREKKEP)
    ax.set_xticks(list(x))
    ax.set_xticklabels([b[0] for b in bulgular], fontsize=11, color=MUREKKEP)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("mAP50 (IoU ≥ 0,5)", fontsize=10.5)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda y, _: v(y, 1)))
    ax.grid(axis="y", color=IZGARA, linewidth=0.8, zorder=0)
    for kenar in ("top", "right", "left"):
        ax.spines[kenar].set_visible(False)
    ax.spines["bottom"].set_color(IZGARA)
    ax.tick_params(axis="y", length=0)
    ax.legend(frameon=False, fontsize=9.5, loc="upper right")
    ax.set_title("Sınıf bazında mAP50: iç test ve dış doğrulama", fontsize=12.5,
                 fontweight="bold", loc="left", color=MUREKKEP)
    fig.text(0.01, 0.012, "Kanal tedavisi: ana model (YOLO26m). Çürük ve periapikal lezyon: "
             "iki aşamalı çürük modeli (YOLO26s).\n" + ATIF, fontsize=7.8, color=IKINCIL,
             linespacing=1.4)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    yol = CIKTI / "sekil2_map50.png"
    fig.savefig(yol, dpi=170, facecolor=YUZEY)
    plt.close(fig)
    return yol, list(zip([b[0] for b in bulgular], ic, dis))


# --------------------------------------------------------------------------- #
# Şekil 3 — örnek çıktı (veri görüntüsü içerir, depoya konmaz)
# --------------------------------------------------------------------------- #

def sekil3(dosya: str = "v59.jpg", esik: float = 0.25):
    from detector import DentalDetector, draw_findings, load_image, summarize
    goruntu = load_image(config.DATA_DIR / "dental_xray" / "test" / "images" / dosya)
    bulgular = DentalDetector().detect(goruntu, conf=esik, codes=["CAR", "END"])
    isaretli = draw_findings(goruntu, bulgular, shape="ellipse")

    fig, ax = plt.subplots(figsize=(13, 7.2))
    fig.patch.set_facecolor(YUZEY)
    ax.imshow(isaretli)
    ax.axis("off")
    ax.set_title(f"Örnek çıktı — test setinden bir röntgen, hassasiyet: Dengeli (eşik {v(esik, 2)})",
                 fontsize=12.5, fontweight="bold", loc="left")
    fig.text(0.01, 0.012, "Kırmızı: çürük, mavi: kanal tedavisi; etiketteki yüzde modelin güven "
             "skorudur, olasılık değildir. Eğitim amaçlıdır, tanı koymaz. " + ATIF,
             fontsize=8, color=IKINCIL)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    yol = CIKTI / "sekil3_ornek_cikti.png"
    fig.savefig(yol, dpi=150, facecolor=YUZEY)
    plt.close(fig)
    return yol, summarize(bulgular)


if __name__ == "__main__":
    print("Kaydedildi:", sekil1())
    y2, sayilar = sekil2()
    print("Kaydedildi:", y2)
    for ad, i, d in sayilar:
        print(f"  {ad:<18} iç {i:.3f}  dış {d:.3f}")
    y3, ozet = sekil3()
    print("Kaydedildi:", y3)
    print("  ", ozet.replace("\n", " | ")[:200])
