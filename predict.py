"""Komut satırından röntgen analizi. İşaretlenmiş görüntüler sonuclar/ klasörüne kaydedilir.

Kullanım:
    python predict.py rontgen.jpg
    python predict.py klasor/ --conf 0.3
    python predict.py rontgen.jpg --all      # dolgu, kron, lezyon vb. diğer bulguları da göster
"""

import argparse
import sys
from pathlib import Path

import config
from detector import DentalDetector, draw_findings, load_image, summarize

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def main():
    ap = argparse.ArgumentParser(description="Diş röntgeninde çürük ve kanal tedavisi tespiti")
    ap.add_argument("inputs", nargs="+", help="röntgen dosyası veya klasörü")
    ap.add_argument("--conf", type=float, default=0.25, help="en düşük güven skoru (0-1)")
    ap.add_argument("--all", action="store_true", help="çürük ve kanal dışındaki bulguları da göster")
    ap.add_argument("--box", action="store_true", help="elips yerine dikdörtgen çiz")
    ap.add_argument("--out", default="sonuclar", help="çıktı klasörü")
    ap.add_argument("--weights", default=str(config.BEST_WEIGHTS))
    args = ap.parse_args()

    files = []
    for p in map(Path, args.inputs):
        files += sorted(q for q in p.iterdir() if q.suffix.lower() in IMG_EXT) if p.is_dir() else [p]
    if not files:
        sys.exit("Görüntü bulunamadı.")

    det = DentalDetector(args.weights)
    codes = None if args.all else config.TARGET_CODES
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)

    for f in files:
        img = load_image(f)
        findings = det.detect(img, conf=args.conf, codes=codes)
        save = out_dir / f"{f.stem}_sonuc.jpg"
        draw_findings(img, findings, shape="box" if args.box else "ellipse").save(save, quality=92)
        print(f"\n{f.name}: {summarize(findings)}")
        for x in findings:
            print(f"  {x.no:>2}. {x.name:<18} güven %{x.confidence * 100:.0f}")
        print(f"  -> {save}")


if __name__ == "__main__":
    main()
