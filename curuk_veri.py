"""Çürüğe özel ikinci model için veri hazırlar.

Ana veri setindeki 14 sınıftan yalnız üçünü (çürük, periapikal lezyon, gömülü diş) alıp
yeniden numaralandırır ve indirilen ek veri setiyle (data/ek_veri) birleştiren yaml dosyalarını yazar.
Ek veri setinde zaten bu üç sınıf 0/1/2 sırasıyla etiketli olduğu için numaralar birebir uyuyor.

Neden ayrı model: ek veri setinde kanal tedavisi, dolgu, kron gibi bulgular etiketsiz. O veriyi
14 sınıflı modele karıştırsaydık model "etiketsiz kanal tedavisi = arka plan" diye öğrenip
en güçlü yeteneğimizi bozacaktı.

Kullanım:
    python curuk_veri.py
"""

import json
import os
import shutil
import sys
from pathlib import Path

import config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ana veri setindeki kod -> yeni sınıf numarası
ESLEME = {"CAR": 0, "API": 1, "IMT": 2}
YENI_ADLAR = ["CAR", "API", "IMT"]          # çürük, periapikal lezyon, gömülü diş
HEDEF = config.DATA_DIR / "curuk"
EK_VERI = config.DATA_DIR / "ek_veri"
IMG_EXT = {".jpg", ".jpeg", ".png"}


def bagla(kaynak: Path, hedef: Path):
    """Diskte yer kaplamasın diye sabit bağlantı; olmazsa kopyala."""
    if hedef.exists():
        return
    try:
        os.link(kaynak, hedef)
    except OSError:
        shutil.copy2(kaynak, hedef)


def bolum_hazirla(kaynak_img: Path, ad: str) -> tuple[int, int]:
    img_dir, lbl_dir = HEDEF / ad / "images", HEDEF / ad / "labels"
    img_dir.mkdir(parents=True, exist_ok=True)
    lbl_dir.mkdir(parents=True, exist_ok=True)
    n_img = n_kutu = 0
    for img in sorted(p for p in kaynak_img.iterdir() if p.suffix.lower() in IMG_EXT):
        etiket = kaynak_img.parent / "labels" / f"{img.stem}.txt"
        if not etiket.exists():
            continue
        satirlar = []
        for satir in etiket.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not satir.strip():
                continue
            parcalar = satir.split()
            kod = config.CLASS_CODES[int(float(parcalar[0]))]
            if kod in ESLEME:
                satirlar.append(" ".join([str(ESLEME[kod]), *parcalar[1:5]]))
        bagla(img, img_dir / img.name)
        (lbl_dir / f"{img.stem}.txt").write_text("\n".join(satirlar) + ("\n" if satirlar else ""),
                                                 encoding="utf-8")
        n_img += 1
        n_kutu += len(satirlar)
    return n_img, n_kutu


def yaml_yaz(yol: Path, train, val: Path, test: Path | None, adlar=None):
    j = lambda p: json.dumps(Path(p).resolve().as_posix(), ensure_ascii=False)
    satirlar = ["# çürük odaklı model için veri tanımı"]
    if isinstance(train, (list, tuple)):
        satirlar.append("train:")
        satirlar += [f"  - {j(p)}" for p in train]
    else:
        satirlar.append(f"train: {j(train)}")
    satirlar.append(f"val: {j(val)}")
    if test is not None:
        satirlar.append(f"test: {j(test)}")
    satirlar.append("names:")
    satirlar += [f"  {i}: {ad}" for i, ad in enumerate(adlar or YENI_ADLAR)]
    yol.write_text("\n".join(satirlar) + "\n", encoding="utf-8")


def main():
    if not config.DATASET_DIR.exists():
        sys.exit("Ana veri seti yok. Önce: python prepare_data.py")

    kaynaklar = {
        "train": config.DATASET_DIR / "train" / "images",
        "valid": config.DATASET_DIR / "valid" / "images",
        "test": config.DATASET_DIR / "test" / "images",
        "external": config.DATASET_DIR / "test_alte_cabinete" / "Ext-validation" / "images",
    }
    print("Ana veri seti 3 sınıfa indirgeniyor (çürük, periapikal lezyon, gömülü diş)...")
    for ad, kaynak in kaynaklar.items():
        n_img, n_kutu = bolum_hazirla(kaynak, ad)
        print(f"  {ad:<10}{n_img:>6} görüntü{n_kutu:>8} kutu")

    ek_img = EK_VERI / "images" / "train"
    ek_sayi = len([p for p in ek_img.iterdir() if p.suffix.lower() in IMG_EXT]) if ek_img.exists() else 0
    if ek_sayi:
        ek_kutu = sum(len([s for s in p.read_text(encoding="utf-8", errors="ignore").splitlines() if s.strip()])
                      for p in (EK_VERI / "labels" / "train").glob("*.txt"))
        print(f"  ek veri  {ek_sayi:>6} görüntü{ek_kutu:>8} kutu")
        egitim = [HEDEF / "train" / "images", ek_img]
    else:
        print("  ek veri bulunamadı, yalnız ana veri seti kullanılacak")
        egitim = HEDEF / "train" / "images"

    yaml_yaz(config.DATA_DIR / "curuk.yaml", egitim, HEDEF / "valid" / "images", HEDEF / "test" / "images")
    yaml_yaz(config.DATA_DIR / "curuk_external.yaml", egitim, HEDEF / "external" / "images", None)
    print(f"\nYazıldı: curuk.yaml, curuk_external.yaml")
    print("Sıradaki adım:")
    print('  python train.py --data data/curuk.yaml --model weights/best.pt --name curuk --nazik --epochs 15')


if __name__ == "__main__":
    main()
