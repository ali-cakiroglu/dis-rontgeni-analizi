"""Veri setini indirir, açar ve YOLO için data yaml dosyalarını hazırlar.

Kullanım:
    python prepare_data.py

Zenodo tek bağlantıda yavaş olduğu için dosya paralel parçalar halinde indirilir.
"""

import hashlib
import json
import random
import shutil
import sys
import threading
import time
import urllib.request
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PIECE = 16 * 1024 * 1024  # her parça 16 MB
WORKERS = 16


def _fetch_range(url, dest, start, end, progress, lock):
    for attempt in range(6):
        written = 0
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
            with urllib.request.urlopen(req, timeout=60) as r, open(dest, "r+b") as f:
                if r.status != 206:
                    raise IOError(f"sunucu parça indirmeyi desteklemedi (HTTP {r.status})")
                f.seek(start)
                while chunk := r.read(1024 * 1024):
                    f.write(chunk)
                    written += len(chunk)
                    with lock:
                        progress[0] += len(chunk)
            if written != end - start + 1:
                raise IOError("parça eksik indi")
            return
        except Exception:  # ağ hatası -> bu parçayı baştan dene
            with lock:
                progress[0] -= written
            if attempt == 5:
                raise
            time.sleep(2 + attempt * 2)


def download(url, dest: Path, size: int):
    part = dest.with_suffix(dest.suffix + ".part")
    with open(part, "wb") as f:
        f.truncate(size)
    ranges = [(s, min(s + PIECE, size) - 1) for s in range(0, size, PIECE)]
    progress, lock = [0], threading.Lock()
    done = threading.Event()

    def report():
        t0 = time.time()
        while not done.wait(15):
            mb = progress[0] / 1e6
            print(f"  {mb:7.1f} / {size / 1e6:.1f} MB  ({mb / (time.time() - t0):.1f} MB/s)", flush=True)

    threading.Thread(target=report, daemon=True).start()
    try:
        with ThreadPoolExecutor(WORKERS) as ex:
            for fut in [ex.submit(_fetch_range, url, part, s, e, progress, lock) for s, e in ranges]:
                fut.result()
    finally:
        done.set()
    part.replace(dest)


def md5sum(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(8 * 1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def find_split_dirs(root: Path) -> dict:
    """images/ klasörlerini bulup train/val/test/external olarak eşler."""
    splits = {}
    for img_dir in sorted(p for p in root.rglob("images") if p.is_dir()):
        key = str(img_dir.relative_to(root)).replace("\\", "/").lower()
        if "ext" in key or "alte_cabinete" in key:
            splits["external"] = img_dir
        elif key.startswith("train") or "/train" in key:
            splits["train"] = img_dir
        elif "valid" in key or key.startswith("val") or "/val" in key:
            splits["val"] = img_dir
        elif "test" in key:
            splits["test"] = img_dir
    return splits


def count_labels(img_dir: Path) -> tuple[int, Counter]:
    lbl_dir = img_dir.parent / "labels"
    counts = Counter()
    n_img = sum(1 for p in img_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"})
    for txt in lbl_dir.glob("*.txt"):
        for line in txt.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip():
                counts[int(float(line.split()[0]))] += 1
    return n_img, counts


def write_yaml(path: Path, root: Path, train: Path, val: Path, test: Path | None, names: list[str]):
    rel = lambda p: p.relative_to(root).as_posix()
    lines = [f"path: {json.dumps(root.as_posix(), ensure_ascii=False)}",
             f"train: {rel(train)}",
             f"val: {rel(val)}"]
    if test is not None:
        lines.append(f"test: {rel(test)}")
    lines.append("names:")
    lines += [f"  {i}: {n}" for i, n in enumerate(names)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    config.DATA_DIR.mkdir(exist_ok=True)
    zip_path = config.DATASET_ZIP

    if not (zip_path.exists() and zip_path.stat().st_size == config.DATASET_SIZE):
        print(f"İndiriliyor: {config.DATASET_URL}\n  ({config.DATASET_SIZE / 1e9:.2f} GB, Zenodo, CC-BY-4.0)")
        download(config.DATASET_URL, zip_path, config.DATASET_SIZE)

    print("MD5 kontrol ediliyor...")
    if md5sum(zip_path) != config.DATASET_MD5:
        zip_path.unlink()
        sys.exit("HATA: dosya bozuk indi (MD5 tutmadı). Scripti tekrar çalıştırın.")

    if not config.DATASET_DIR.exists():
        print(f"Açılıyor -> {config.DATASET_DIR}")
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(config.DATASET_DIR)

    splits = find_split_dirs(config.DATASET_DIR)
    missing = {"train", "val", "test"} - splits.keys()
    if missing:
        sys.exit(f"HATA: şu bölümler bulunamadı: {missing}. Bulunanlar: {splits}")

    root = config.DATASET_DIR
    names = config.CLASS_CODES
    write_yaml(config.DATA_YAML, root, splits["train"], splits["val"], splits["test"], names)
    if "external" in splits:
        # Ultralytics 'train' anahtarı istiyor; dış set 'val' olarak değerlendirilir.
        write_yaml(config.EXTERNAL_YAML, root, splits["train"], splits["external"], None, names)
    print(f"Yazıldı: {config.DATA_YAML.name}" + (f", {config.EXTERNAL_YAML.name}" if "external" in splits else ""))

    print(f"\n{'Bölüm':<10}{'Röntgen':>9}{'Çürük':>8}{'Kanal':>8}{'Toplam kutu':>13}")
    car, end = names.index("CAR"), names.index("END")
    for key in ("train", "val", "test", "external"):
        if key in splits:
            n_img, c = count_labels(splits[key])
            print(f"{key:<10}{n_img:>9}{c[car]:>8}{c[end]:>8}{sum(c.values()):>13}")

    # Arayüzde "örnek" olarak kullanılacak birkaç test röntgeni
    config.EXAMPLES_DIR.mkdir(exist_ok=True)
    if not any(config.EXAMPLES_DIR.iterdir()):
        test_imgs = sorted(p for p in splits["test"].iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
        for p in random.Random(0).sample(test_imgs, k=min(4, len(test_imgs))):
            shutil.copy2(p, config.EXAMPLES_DIR / p.name)
        print(f"\nÖrnek röntgenler kopyalandı -> {config.EXAMPLES_DIR.name}/")

    print("\nHazır. Sıradaki adım: python train.py")


if __name__ == "__main__":
    main()
