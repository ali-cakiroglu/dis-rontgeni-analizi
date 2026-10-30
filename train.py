"""YOLO modelini diş röntgeni veri setiyle eğitir, sonra test setinde değerlendirir.

Kullanım:
    python train.py                         # varsayılan model (config.DEFAULT_MODEL)
    python train.py --model yolov8s.pt      # YOLOv8 ile
    python train.py --epochs 150 --imgsz 1280
    python train.py --resume                # yarıda kalan son eğitime devam et
    python train.py --auto-resume           # yarım eğitim varsa devam et, yoksa yeni başlat (Colab)
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

import config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def gentle_mode(vram_fraction: float = 0.8, threads: int = 4):
    """Bilgisayarı yormayan mod: eğitim arka planda kalsın, ekran kartını ve işlemciyi tamamen kapmasın.

    Donanıma zarar vermeyi engellemez (buna zaten gerek yok, kart kendini korur); amacı bilgisayarı
    eğitim sırasında kullanılabilir tutmak: düşük süreç önceliği ve sınırlı VRAM. Öncelik düşük
    olduğu için açtığın programlar eğitimin önüne geçer.
    """
    import psutil
    import torch

    try:
        proc = psutil.Process()
        proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 10)
    except Exception as e:
        print(f"Öncelik düşürülemedi: {e}")
    torch.set_num_threads(threads)
    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(vram_fraction)
        total = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"Nazik mod: düşük öncelik, {threads} çekirdek, en fazla {vram_fraction * total:.1f} GB VRAM")


def batch_arg(v: str):
    f = float(v)
    return int(f) if f.is_integer() else f


def unfinished_run() -> Path | None:
    """runs/ altında yarıda kalmış en yeni eğitimin last.pt dosyası (biten eğitimlerde epoch = -1 olur)."""
    from ultralytics.utils.patches import torch_load

    for last in sorted(config.RUNS_DIR.glob("*/weights/last.pt"), key=lambda p: p.stat().st_mtime, reverse=True):
        if torch_load(last, map_location="cpu").get("epoch", -1) != -1:
            return last
    return None


def main():
    ap = argparse.ArgumentParser(description="Diş röntgeni tespit modeli eğitimi")
    ap.add_argument("--model", default=config.DEFAULT_MODEL,
                    help="yolov8s.pt, yolo11s.pt, yolo26s.pt ... (n/s/m/l/x = küçükten büyüğe)")
    ap.add_argument("--data", default=None, help="veri tanımı yaml dosyası (varsayılan: data/dental.yaml)")
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--imgsz", type=int, default=config.IMGSZ, help="eğitim çözünürlüğü (piksel)")
    ap.add_argument("--batch", type=batch_arg, default=-1,
                    help="-1: GPU belleğine göre otomatik, 0.8: belleğin %%80'i, 8: sabit")
    ap.add_argument("--patience", type=int, default=30, help="bu kadar epoch iyileşme olmazsa dur")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--cache", choices=["ram", "disk"], default=None,
                    help="ram: görüntüleri belleğe al (Colab/Linux'ta hızlandırır; Windows'ta önerilmez)")
    ap.add_argument("--fraction", type=float, default=1.0, help="verinin bir kısmıyla hızlı deneme (ör. 0.05)")
    ap.add_argument("--device", default=None, help="0 = ilk GPU, cpu = işlemci")
    ap.add_argument("--name", default=None, help="runs/ altındaki klasör adı")
    ap.add_argument("--cikti", default="best.pt", help="weights/ altına kopyalanacak dosya adı")
    ap.add_argument("--resume", nargs="?", const="auto", default=None,
                    help="yarıda kalan eğitime devam et (isteğe bağlı: last.pt yolu)")
    ap.add_argument("--auto-resume", action="store_true",
                    help="yarım kalmış eğitim varsa ona devam et, yoksa yeni eğitim başlat")
    ap.add_argument("--nazik", action="store_true",
                    help="bilgisayarı yormayan mod: düşük öncelik, az çekirdek, sınırlı VRAM (daha yavaş eğitir)")
    args = ap.parse_args()

    veri_yaml = Path(args.data) if args.data else config.DATA_YAML
    if not veri_yaml.exists():
        sys.exit(f"Veri tanımı bulunamadı: {veri_yaml}. Önce: python prepare_data.py")

    if args.nazik:
        # 6 GB'lık kartlarda 1024 pikselde otomatik batch seçimi (batch=-1) profilleme sırasında
        # belleği taşırıp batch'i 1'e düşürebiliyor; 4 ölçülmüş güvenli değer (~3.3 GB).
        gentle_mode()
        if args.batch == -1:
            args.batch = 4
        args.workers = min(args.workers, 4)  # Windows: her isci torch'u ayri yukler, 8 isci sistem bellegini tuketiyor

    from ultralytics import YOLO

    last = None
    if args.resume and args.resume != "auto":
        last = Path(args.resume)
    elif args.resume or args.auto_resume:
        last = unfinished_run()
        if last is None and args.resume:
            sys.exit(f"Devam edilecek yarım eğitim bulunamadı ({config.RUNS_DIR}).")

    if last:
        print(f"Yarıda kalan eğitime devam ediliyor: {last}")
        model = YOLO(str(last))
        model.train(resume=True)
    else:
        model = YOLO(args.model)
        model.train(
            data=str(veri_yaml),
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            patience=args.patience,
            workers=args.workers,
            cache=args.cache or False,
            fraction=args.fraction,
            device=args.device,
            project=str(config.RUNS_DIR),
            name=args.name or Path(args.model).stem,
            seed=0,
            plots=True,
        )

    best = Path(model.trainer.best)
    config.WEIGHTS_DIR.mkdir(exist_ok=True)
    hedef = config.WEIGHTS_DIR / args.cikti
    shutil.copy2(best, hedef)
    print(f"\nEn iyi model kopyalandı: {best} -> {hedef}")

    from evaluate import evaluate
    dis = veri_yaml.with_name(veri_yaml.stem + "_external.yaml")
    evaluate(hedef, imgsz=model.trainer.args.imgsz,
             data_yaml=veri_yaml, external_yaml=dis if dis.exists() else None,
             metrics_file=config.WEIGHTS_DIR / (Path(args.cikti).stem + "_metrics.json"))


if __name__ == "__main__":
    main()
