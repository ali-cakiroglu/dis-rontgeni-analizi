"""Model yükleme, tespit ve sonuçları röntgen üzerine çizme."""

from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

import config


@dataclass
class Finding:
    no: int
    code: str            # veri setindeki sınıf kodu (CAR, END, ...)
    name: str            # Türkçe adı
    confidence: float    # modelin güven skoru (0-1)
    box: tuple[float, float, float, float]  # x1, y1, x2, y2 (piksel)


def load_image(source) -> Image.Image:
    """Dosya yolu, PIL görüntüsü veya numpy (RGB) dizisini RGB PIL görüntüsüne çevirir."""
    if isinstance(source, (str, Path)):
        img = Image.open(source)
    elif isinstance(source, np.ndarray):
        img = Image.fromarray(source)
    else:
        img = source
    img = ImageOps.exif_transpose(img)  # telefonla çekilen fotoğraflarda yönü düzeltir
    if img.mode in ("I;16", "I;16B", "I;16L", "I", "F"):
        # 16 bit röntgen çıktıları: 8 bite ölçekle, yoksa görüntü bembeyaz olur
        arr = np.asarray(img, dtype=np.float32)
        lo, hi = np.percentile(arr, (0.5, 99.5))
        arr = np.clip((arr - lo) / max(hi - lo, 1e-6) * 255, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)
    return img.convert("RGB")


class DentalDetector:
    """14 sınıflı ana model; çürük ve periapikal lezyon için varsa ikinci (daha iyi) model.

    İkinci model dış doğrulamada çürükte belirgin şekilde daha iyi olduğu için o iki bulguyu
    ondan, geri kalan 12 bulguyu ana modelden alıyoruz.
    """

    def __init__(self, weights: Path | str = config.BEST_WEIGHTS, device=None,
                 curuk_weights: Path | str | None = config.CURUK_WEIGHTS):
        from ultralytics import YOLO

        weights = Path(weights)
        if not weights.exists():
            raise FileNotFoundError(
                f"Model dosyası bulunamadı: {weights}\n"
                "Önce 'python prepare_data.py' ve 'python train.py' çalıştırın."
            )
        self.model = YOLO(str(weights))
        self.device = device
        self.names = self.model.names  # {0: 'IMP', 1: 'PRR', ...}
        self.code_to_id = {code: i for i, code in self.names.items()}

        self.curuk_model = None
        self.curuk_codes: list[str] = []
        yol = Path(curuk_weights) if curuk_weights else None
        if yol and yol.exists():
            self.curuk_model = YOLO(str(yol))
            self.curuk_names = self.curuk_model.names
            self.curuk_code_to_id = {code: i for i, code in self.curuk_names.items()}
            self.curuk_codes = [c for c in config.CURUK_CODES if c in self.curuk_code_to_id]
        # Model hangi çözünürlükte eğitildiyse tahminde de onu kullan (1024, 1280...)
        args = getattr(self.model.model, "args", {}) or {}
        value = args.get("imgsz") if isinstance(args, dict) else getattr(args, "imgsz", None)
        self.imgsz = int(value) if value else config.IMGSZ

    def detect(self, image, conf: float = 0.25, codes=config.TARGET_CODES,
               imgsz: int | None = None) -> list[Finding]:
        """codes=None ise bütün sınıflar döner."""
        imgsz = imgsz or self.imgsz
        img = load_image(image)
        istenen = list(codes) if codes else list(self.names.values())
        findings = []

        # Çürük ve periapikal lezyon ikinci modelden, kalanlar ana modelden
        ana_kodlar = [c for c in istenen if c not in self.curuk_codes and c in self.code_to_id]
        if ana_kodlar:
            findings += self._tahmin(self.model, self.names, img, conf, imgsz,
                                     [self.code_to_id[c] for c in ana_kodlar])
        curuk_kodlar = [c for c in istenen if c in self.curuk_codes]
        if curuk_kodlar:
            findings += self._tahmin(self.curuk_model, self.curuk_names, img, conf, imgsz,
                                     [self.curuk_code_to_id[c] for c in curuk_kodlar])
        return select(findings)

    def _tahmin(self, model, names, img, conf, imgsz, class_ids) -> list[Finding]:
        result = model.predict(img, conf=conf, imgsz=imgsz, classes=class_ids, max_det=1000,
                               device=self.device, verbose=False)[0]
        out = []
        for (x1, y1, x2, y2), c, s in zip(result.boxes.xyxy.tolist(),
                                          result.boxes.cls.tolist(),
                                          result.boxes.conf.tolist()):
            code = names[int(c)]
            out.append(Finding(0, code, config.tr_name(code), float(s), (x1, y1, x2, y2)))
        return out


def select(findings: list[Finding], conf: float = 0.0, codes=None) -> list[Finding]:
    """Güven eşiği ve sınıfa göre süzer; soldan sağa 1, 2, 3... diye yeniden numaralandırır.

    Arayüz modeli bir kez düşük eşikle çalıştırıp kaydırıcı değiştikçe sadece bunu çağırır.
    """
    out = [replace(f) for f in findings if f.confidence >= conf and (codes is None or f.code in codes)]
    out.sort(key=lambda f: (f.box[0] + f.box[2]) / 2)
    for i, f in enumerate(out, 1):
        f.no = i
    return out


def _font(size: int):
    for name in ("arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def _overlaps(a, b, pad=2):
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])


def _shape_bounds(f: Finding, shape: str, min_r: float):
    x1, y1, x2, y2 = f.box
    if shape != "ellipse":
        return x1, y1, x2, y2
    # Kutunun köşeleri de içeride kalsın diye elipsi biraz büyüt
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    rx = max((x2 - x1) / 2 * 1.3, min_r)
    ry = max((y2 - y1) / 2 * 1.3, min_r)
    return cx - rx, cy - ry, cx + rx, cy + ry


def draw_findings(image, findings: list[Finding], shape: str = "ellipse",
                  show_labels: bool = True) -> Image.Image:
    """Bulguları elips (ya da kutu) içine alır, yanına 'No. Ad %güven' etiketi yazar."""
    img = load_image(image).copy()
    W, H = img.size
    scale = min(W, H)
    line = max(2, round(scale / 260))
    font = _font(max(12, round(scale / 45)))
    draw = ImageDraw.Draw(img)
    bounds = {id(f): _shape_bounds(f, shape, scale / 90) for f in findings}

    for f in findings:
        color = config.COLORS.get(f.code, (255, 255, 255))
        if shape == "ellipse":
            draw.ellipse(bounds[id(f)], outline=color, width=line)
        else:
            draw.rectangle(bounds[id(f)], outline=color, width=line)

    if not show_labels:
        return img

    # Etiket yeri: şeklin üstü > altı > sağı > solu; hepsi doluysa yukarı doğru kaydır
    placed = []
    pad = max(2, line)
    for f in sorted(findings, key=lambda f: -f.confidence):
        color = config.COLORS.get(f.code, (255, 255, 255))
        text = f"{f.no}. {f.name} %{f.confidence * 100:.0f}"
        tb = draw.textbbox((0, 0), text, font=font)
        tw, th = tb[2] - tb[0] + 2 * pad, tb[3] - tb[1] + 2 * pad
        sx1, sy1, sx2, sy2 = bounds[id(f)]
        cx, cy = (sx1 + sx2) / 2, (sy1 + sy2) / 2

        def clamp(lx, ly):
            lx, ly = min(max(0, lx), W - tw), min(max(0, ly), H - th)
            return lx, ly, lx + tw, ly + th

        options = [clamp(cx - tw / 2, sy1 - th - line), clamp(cx - tw / 2, sy2 + line),
                   clamp(sx2 + line, cy - th / 2), clamp(sx1 - tw - line, cy - th / 2)]
        options += [clamp(cx - tw / 2, sy1 - th - line - k * (th + line)) for k in range(1, 12)]
        idx = next((i for i, r in enumerate(options) if not any(_overlaps(r, p) for p in placed)), 0)
        rect = options[idx]
        placed.append(rect)
        if idx >= 4:  # etiket şekilden uzaklaştıysa bağlantı çizgisi çek
            draw.line(((rect[0] + rect[2]) / 2, rect[3], cx, sy1), fill=color, width=max(1, line // 2))
        draw.rectangle(rect, fill=color)
        text_color = (0, 0, 0) if sum(color) > 450 else (255, 255, 255)
        draw.text((rect[0] + pad - tb[0], rect[1] + pad - tb[1]), text, font=font, fill=text_color)
    return img


def crop_finding(image, f: Finding, out_width: int = 420) -> Image.Image:
    """Bulgunun etrafından yakın plan kesit çıkarır (küçük lezyonları gözle kontrol etmek için)."""
    img = load_image(image)
    W, H = img.size
    x1, y1, x2, y2 = f.box
    pad = max(x2 - x1, y2 - y1) * 0.9 + min(W, H) / 60
    kesit = (max(0, x1 - pad), max(0, y1 - pad), min(W, x2 + pad), min(H, y2 + pad))
    parca = img.crop(tuple(round(v) for v in kesit))
    oran = out_width / max(parca.width, 1)
    parca = parca.resize((out_width, max(1, round(parca.height * oran))), Image.LANCZOS)

    draw = ImageDraw.Draw(parca)
    cx, cy = ((x1 + x2) / 2 - kesit[0]) * oran, ((y1 + y2) / 2 - kesit[1]) * oran
    rx, ry = (x2 - x1) / 2 * 1.3 * oran, (y2 - y1) / 2 * 1.3 * oran
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry),
                 outline=config.COLORS.get(f.code, (255, 255, 255)), width=3)
    return parca


def summarize(findings: list[Finding]) -> str:
    if not findings:
        return "Seçili bulgulardan hiçbiri tespit edilmedi."
    counts = {}
    for f in findings:
        counts[f.name] = counts.get(f.name, 0) + 1
    return ", ".join(f"{n} {name}" for name, n in counts.items())
