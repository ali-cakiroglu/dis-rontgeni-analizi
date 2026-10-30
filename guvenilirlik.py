"""Modelin ne kadar güvenilir olduğunu anlaşılır sayılarla çıkarır.

Her güven eşiği için: kaç bulguyu doğru yakaladı, kaç tane yanlış alarm verdi, kaçını kaçırdı.
Ayrıca yanlış alarmların neyin üzerine düştüğünü (dolgu mu, kron mu, boş bölge mi) sayar.

Kullanım:
    python guvenilirlik.py                      # dış doğrulama seti (başka klinikler) - varsayılan
    python guvenilirlik.py --split test         # iç test seti (aynı klinik)
    python guvenilirlik.py --split both
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import config
from detector import DentalDetector, load_image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ESIKLER = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60]
IOU_ESIK = 0.5        # tahmin ile gerçek kutu bu oranda örtüşürse "aynı diş" sayılır
IOU_YAKIN = 0.3       # yanlış alarmın neyin üzerine düştüğünü ararken daha gevşek


def iou(a, b) -> float:
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    kesisim = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    if kesisim <= 0:
        return 0.0
    alan_a = (a[2] - a[0]) * (a[3] - a[1])
    alan_b = (b[2] - b[0]) * (b[3] - b[1])
    return kesisim / (alan_a + alan_b - kesisim)


def gercek_kutular(label_path: Path, w: int, h: int) -> list[tuple[str, tuple]]:
    kutular = []
    for satir in label_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not satir.strip():
            continue
        c, cx, cy, bw, bh = satir.split()[:5]
        code = config.CLASS_CODES[int(float(c))]
        cx, cy, bw, bh = float(cx) * w, float(cy) * h, float(bw) * w, float(bh) * h
        kutular.append((code, (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)))
    return kutular


def topla(det: DentalDetector, img_dir: Path, codes: list[str]) -> dict:
    """Her tahmini (güven, doğru mu, neyin üstüne düştü) olarak kaydeder; eşik süzmesi sonra yapılır."""
    sonuc = {c: {"eslesmeler": [], "gercek": 0} for c in codes}
    resimler = sorted(p for p in img_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    goruntu_basi = {c: [] for c in codes}        # (gerçek kutu sayısı, [(güven, doğru mu)])

    for i, p in enumerate(resimler, 1):
        if i % 25 == 0 or i == len(resimler):
            print(f"  {i}/{len(resimler)} röntgen işlendi", flush=True)
        img = load_image(p)
        w, h = img.size
        gt_hepsi = gercek_kutular(img_dir.parent / "labels" / f"{p.stem}.txt", w, h)
        tahminler = det.detect(img, conf=0.01, codes=codes)

        for code in codes:
            gt = [kutu for kod, kutu in gt_hepsi if kod == code]
            sonuc[code]["gercek"] += len(gt)
            kullanildi = [False] * len(gt)
            kayitlar = []
            for f in sorted((f for f in tahminler if f.code == code), key=lambda f: -f.confidence):
                en_iyi, en_iyi_iou = -1, IOU_ESIK
                for j, kutu in enumerate(gt):
                    if not kullanildi[j]:
                        o = iou(f.box, kutu)
                        if o >= en_iyi_iou:
                            en_iyi, en_iyi_iou = j, o
                if en_iyi >= 0:
                    kullanildi[en_iyi] = True
                    kayitlar.append((f.confidence, True, None))
                else:
                    # yanlış alarm neyin üstüne düştü?
                    ust = max(((kod, iou(f.box, kutu)) for kod, kutu in gt_hepsi if kod != code),
                              key=lambda x: x[1], default=(None, 0.0))
                    kayitlar.append((f.confidence, False, ust[0] if ust[1] >= IOU_YAKIN else "boş bölge"))
            sonuc[code]["eslesmeler"] += kayitlar
            goruntu_basi[code].append((len(gt), kayitlar))
    return {"siniflar": sonuc, "goruntu_basi": goruntu_basi, "resim_sayisi": len(resimler)}


def tablo(veri: dict, code: str, esik_detay: float):
    s = veri["siniflar"][code]
    n_img = veri["resim_sayisi"]
    print(f"\n=== {config.tr_name(code).upper()} — {n_img} röntgen, {s['gercek']} gerçek bulgu ===")
    print(f"{'Eşik':>6}{'İşaret':>9}{'Doğru':>8}{'Yanlış':>8}{'Kaçan':>8}"
          f"{'Kesinlik':>10}{'Duyarlılık':>12}{'Röntgen başına yanlış':>23}")
    for esik in ESIKLER:
        secilen = [k for k in s["eslesmeler"] if k[0] >= esik]
        tp = sum(1 for k in secilen if k[1])
        fp = len(secilen) - tp
        kesinlik = tp / len(secilen) if secilen else 0.0
        duyarlilik = tp / s["gercek"] if s["gercek"] else 0.0
        print(f"{esik:>6.2f}{len(secilen):>9}{tp:>8}{fp:>8}{s['gercek'] - tp:>8}"
              f"{kesinlik:>9.0%}{duyarlilik:>11.0%}{fp / n_img:>21.2f}")

    yanlislar = Counter(k[2] for k in s["eslesmeler"] if not k[1] and k[0] >= esik_detay)
    toplam = sum(yanlislar.values())
    if toplam:
        print(f"\n  Yanlış alarmlar neyin üstüne düşüyor? (eşik {esik_detay:.2f}, {toplam} yanlış işaret)")
        for kod, adet in yanlislar.most_common(5):
            ad = "boş bölge / sağlam diş" if kod == "boş bölge" else config.tr_name(kod)
            print(f"    {ad:<28}{adet:>6}  (%{adet / toplam * 100:.0f})")


def goruntu_ozeti(veri: dict, code: str, esik: float):
    """Röntgen (hasta) bazında: bu röntgende bulgu var mı sorusuna verdiği cevabın doğruluğu."""
    tam = temiz = dogru_pozitif = yanlis_pozitif = dogru_negatif = yanlis_negatif = 0
    for gt_sayisi, kayitlar in veri["goruntu_basi"][code]:
        secilen = [k for k in kayitlar if k[0] >= esik]
        tp = sum(1 for k in secilen if k[1])
        fp = len(secilen) - tp
        if gt_sayisi and tp == gt_sayisi:
            tam += 1
        if fp == 0:
            temiz += 1
        isaretledi = len(secilen) > 0
        if gt_sayisi and isaretledi:
            dogru_pozitif += 1
        elif gt_sayisi:
            yanlis_negatif += 1
        elif isaretledi:
            yanlis_pozitif += 1
        else:
            dogru_negatif += 1

    toplam = len(veri["goruntu_basi"][code])
    var_olan = dogru_pozitif + yanlis_negatif
    yok_olan = dogru_negatif + yanlis_pozitif
    print(f"\n  Eşik {esik:.2f} — röntgen (hasta) bazında:")
    if var_olan:
        print(f"    Bulgu olan {var_olan} röntgenin {dogru_pozitif}'inde ({dogru_pozitif / var_olan:.0%}) "
              f"en az birini yakaladı, {tam}'inde ({tam / var_olan:.0%}) hepsini buldu")
    if yok_olan:
        print(f"    Hiç bulgu olmayan {yok_olan} röntgenin {dogru_negatif}'inde ({dogru_negatif / yok_olan:.0%}) "
              f"doğru şekilde 'temiz' dedi")
    print(f"    {toplam} röntgenin {temiz}'inde ({temiz / toplam:.0%}) hiç yanlış işaret yok")


def main():
    ap = argparse.ArgumentParser(description="Model güvenilirlik tablosu")
    ap.add_argument("--split", choices=["external", "test", "both"], default="external")
    ap.add_argument("--weights", default=str(config.BEST_WEIGHTS))
    ap.add_argument("--esik", type=float, default=0.15, help="röntgen bazlı özet için eşik")
    args = ap.parse_args()

    yollar = {
        "test": (config.DATASET_DIR / "test" / "images", "İÇ TEST SETİ (aynı klinik, aynı cihaz)"),
        "external": (config.DATASET_DIR / "test_alte_cabinete" / "Ext-validation" / "images",
                     "DIŞ DOĞRULAMA (başka klinikler, farklı cihazlar) — hastaneden getireceğin röntgene en yakın senaryo"),
    }
    secilen = ["test", "external"] if args.split == "both" else [args.split]

    det = DentalDetector(args.weights)
    print(f"Model: {Path(args.weights).name} (çözünürlük {det.imgsz})")
    cikti = {}
    for anahtar in secilen:
        img_dir, baslik = yollar[anahtar]
        print(f"\n########## {baslik}")
        veri = topla(det, img_dir, config.TARGET_CODES)
        for code in config.TARGET_CODES:
            tablo(veri, code, args.esik)
            goruntu_ozeti(veri, code, args.esik)
        # Ham kayıtlar: (güven, doğru mu, yanlışsa neyin üstünde) - başka eşikleri sonradan hesaplamak için
        cikti[anahtar] = {
            "resim": veri["resim_sayisi"],
            "siniflar": {code: {"gercek": veri["siniflar"][code]["gercek"],
                                "tahminler": [[round(c, 4), t, u] for c, t, u in veri["siniflar"][code]["eslesmeler"]]}
                         for code in config.TARGET_CODES},
        }

    yol = config.WEIGHTS_DIR / "guvenilirlik.json"
    yol.write_text(json.dumps(cikti, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nKaydedildi: {yol}")


if __name__ == "__main__":
    main()
