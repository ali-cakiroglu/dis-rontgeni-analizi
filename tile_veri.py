"""Panoramik röntgenleri üst üste binen parçalara böler (tiling).

Neden: çürük panoramik röntgende ~78x103 piksellik bir leke. Görüntü 1024 pikselde modele
verilince 0,37 ile küçülüyor ve lezyon ~29x38 piksele iniyor. Röntgeni 6 parçaya bölüp her
parçayı ayrı ayrı 1024 pikselde işlersek küçülme oranı 0,92'ye çıkıyor ve lezyon ~72x95 piksel
kalıyor — yani modele 2,5 kat daha büyük görünüyor.

Parçalar %20 üst üste biner; sınıra denk gelen lezyonlar en az bir parçada tam görünür.

Kullanım:
    python tile_veri.py
"""

import json
import random
import sys
from pathlib import Path

from PIL import Image

import argparse

import config
from curuk_veri import HEDEF as CURUK_DIR, YENI_ADLAR, yaml_yaz

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SUTUN, SATIR, BINDIRME = 3, 2, 0.20     # 6 parça, %20 üst üste binme
EN_AZ_KALAN = 0.40                      # kutunun bu oranından azı kaldıysa parçaya yazma
BOS_PARCA_ORANI = 0.35                  # eğitimde bulgusuz parçaların ne kadarı tutulsun
HEDEF = config.DATA_DIR / "tile"
IMG_EXT = {".jpg", ".jpeg", ".png"}

# Hangi veriden parça üretilecek: 3 sınıflı çürük seti ya da 14 sınıflı ana set
KAYNAKLAR = {
    "curuk": {"dizin": CURUK_DIR, "adlar": YENI_ADLAR, "hedef": "tile", "yaml": "tile"},
    "ana": {"dizin": None, "adlar": config.CLASS_CODES, "hedef": "tile14", "yaml": "tile14"},
}
ANA_BOLUMLER = {"train": "train", "valid": "valid", "test": "test",
                "external": "test_alte_cabinete/Ext-validation"}


def parcalar(w: int, h: int):
    """(x0, y0, x1, y1) listesi döndürür."""
    pw = w / (SUTUN - (SUTUN - 1) * BINDIRME)
    ph = h / (SATIR - (SATIR - 1) * BINDIRME)
    adim_x, adim_y = pw * (1 - BINDIRME), ph * (1 - BINDIRME)
    out = []
    for sy in range(SATIR):
        for sx in range(SUTUN):
            x0, y0 = round(sx * adim_x), round(sy * adim_y)
            out.append((x0, y0, min(round(x0 + pw), w), min(round(y0 + ph), h)))
    return out


def bolum(ad: str, rastgele: random.Random, kok: Path, alt: str) -> tuple[int, int, int]:
    kaynak = kok / alt
    img_dir, lbl_dir = HEDEF / ad / "images", HEDEF / ad / "labels"
    img_dir.mkdir(parents=True, exist_ok=True)
    lbl_dir.mkdir(parents=True, exist_ok=True)
    n_parca = n_kutu = n_bos = 0

    for img_yolu in sorted(p for p in (kaynak / "images").iterdir() if p.suffix.lower() in IMG_EXT):
        etiket = kaynak / "labels" / f"{img_yolu.stem}.txt"
        if not etiket.exists():
            continue
        img = Image.open(img_yolu)
        W, H = img.size
        kutular = []
        for satir in etiket.read_text(encoding="utf-8").splitlines():
            if satir.strip():
                c, cx, cy, bw, bh = satir.split()[:5]
                cx, cy, bw, bh = float(cx) * W, float(cy) * H, float(bw) * W, float(bh) * H
                kutular.append((int(c), cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2))

        for i, (x0, y0, x1, y1) in enumerate(parcalar(W, H)):
            pw, ph = x1 - x0, y1 - y0
            satirlar = []
            for c, bx0, by0, bx1, by1 in kutular:
                kx0, ky0 = max(bx0, x0), max(by0, y0)
                kx1, ky1 = min(bx1, x1), min(by1, y1)
                if kx1 <= kx0 or ky1 <= ky0:
                    continue
                kalan = ((kx1 - kx0) * (ky1 - ky0)) / max((bx1 - bx0) * (by1 - by0), 1e-6)
                if kalan < EN_AZ_KALAN:
                    continue
                cx, cy = ((kx0 + kx1) / 2 - x0) / pw, ((ky0 + ky1) / 2 - y0) / ph
                satirlar.append(f"{c} {cx:.6f} {cy:.6f} {(kx1 - kx0) / pw:.6f} {(ky1 - ky0) / ph:.6f}")

            if not satirlar:
                n_bos += 1
                if ad == "train" and rastgele.random() > BOS_PARCA_ORANI:
                    continue
            ad_dosya = f"{img_yolu.stem}_p{i}"
            img.crop((x0, y0, x1, y1)).convert("RGB").save(img_dir / f"{ad_dosya}.jpg", quality=92)
            (lbl_dir / f"{ad_dosya}.txt").write_text("\n".join(satirlar) + ("\n" if satirlar else ""),
                                                     encoding="utf-8")
            n_parca += 1
            n_kutu += len(satirlar)
    return n_parca, n_kutu, n_bos


def main():
    ap = argparse.ArgumentParser(description="Röntgenleri parçalara böl")
    ap.add_argument("--kaynak", choices=list(KAYNAKLAR), default="curuk",
                    help="curuk: 3 sınıflı çürük seti | ana: 14 sınıflı ana set")
    args = ap.parse_args()
    secim = KAYNAKLAR[args.kaynak]
    kok = secim["dizin"] or config.DATASET_DIR
    adlar = secim["adlar"]
    global HEDEF
    HEDEF = config.DATA_DIR / secim["hedef"]
    bolumler = ANA_BOLUMLER if args.kaynak == "ana" else {b: b for b in ("train", "valid", "test", "external")}
    if not (kok / list(bolumler.values())[0] / "images").exists():
        sys.exit(f"Kaynak veri bulunamadı: {kok}")
    rastgele = random.Random(0)
    print(f"Röntgenler {SUTUN}x{SATIR} = {SUTUN * SATIR} parçaya bölünüyor (%{BINDIRME * 100:.0f} bindirme)...")
    for ad, alt in bolumler.items():
        n, k, b = bolum(ad, rastgele, kok, alt)
        print(f"  {ad:<10}{n:>7} parça{k:>8} kutu   (bulgusuz parça: {b})")

    y = secim["yaml"]
    yaml_yaz(config.DATA_DIR / f"{y}.yaml", HEDEF / "train" / "images",
             HEDEF / "valid" / "images", HEDEF / "test" / "images", adlar)
    yaml_yaz(config.DATA_DIR / f"{y}_external.yaml", HEDEF / "train" / "images",
             HEDEF / "external" / "images", None, adlar)
    (HEDEF / "parca_duzeni.json").write_text(
        json.dumps({"sutun": SUTUN, "satir": SATIR, "bindirme": BINDIRME}), encoding="utf-8")
    print("\nYazıldı: tile.yaml, tile_external.yaml")
    print("Sıradaki adım:")
    print("  python train.py --data data/tile.yaml --model weights/curuk2.pt --name tile "
          "--cikti tile.pt --nazik --epochs 15 --patience 6")


if __name__ == "__main__":
    main()
