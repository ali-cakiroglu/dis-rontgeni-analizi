"""Ekran kartı ısınırsa eğitimi duraklatır, soğuyunca devam ettirir.

Donanım zaten 102 °C'de kendini korur; bu bekçi bilgisayarı daha serin tutmak için
daha erken devreye girer. Eğitim süreci askıya alınır (öldürülmez), soğuyunca kaldığı
yerden devam eder.

Kullanım (eğitim çalışırken, ayrı pencerede):
    python isi_bekcisi.py
    python isi_bekcisi.py --durdur 80 --devam 70
"""

import argparse
import ctypes
import subprocess
import sys
import time
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROCESS_SUSPEND_RESUME = 0x0800
kernel32 = ctypes.windll.kernel32
ntdll = ctypes.windll.ntdll


def gpu_sicaklik() -> int | None:
    try:
        c = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
                           capture_output=True, text=True, timeout=10)
        return int(c.stdout.strip().splitlines()[0])
    except Exception:
        return None


def egitim_pidleri() -> list[int]:
    """Bu projenin sanal ortamından çalışan train.py süreçleri."""
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
          "Where-Object { $_.CommandLine -like '*train.py*' -and $_.CommandLine -like '*Görüntü*' } | "
          "Select-Object -ExpandProperty ProcessId")
    try:
        c = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                           capture_output=True, text=True, timeout=20)
        return [int(s) for s in c.stdout.split() if s.strip().isdigit()]
    except Exception:
        return []


def islem(pid: int, durdur: bool) -> bool:
    h = kernel32.OpenProcess(PROCESS_SUSPEND_RESUME, False, pid)
    if not h:
        return False
    (ntdll.NtSuspendProcess if durdur else ntdll.NtResumeProcess)(h)
    kernel32.CloseHandle(h)
    return True


def main():
    ap = argparse.ArgumentParser(description="Isı bekçisi")
    ap.add_argument("--durdur", type=int, default=83, help="bu sıcaklıkta duraklat (°C)")
    ap.add_argument("--devam", type=int, default=73, help="bu sıcaklığa düşünce devam et (°C)")
    ap.add_argument("--aralik", type=int, default=20, help="kaç saniyede bir bakılsın")
    a = ap.parse_args()

    print(f"Isı bekçisi çalışıyor: {a.durdur} °C'de duraklat, {a.devam} °C'de devam et. Çıkmak için Ctrl+C.")
    duraklatildi, ustuste = False, 0
    while True:
        t = gpu_sicaklik()
        pidler = egitim_pidleri()
        if t is None or not pidler:
            if duraklatildi:
                duraklatildi = False
            time.sleep(a.aralik)
            continue

        damga = datetime.now().strftime("%H:%M")
        if not duraklatildi:
            ustuste = ustuste + 1 if t >= a.durdur else 0
            if ustuste >= 3:                      # geçici sıçramalarda duraklatma
                for pid in pidler:
                    islem(pid, True)
                duraklatildi, ustuste = True, 0
                print(f"[{damga}] {t} °C — soğuma molası verildi ({len(pidler)} süreç duraklatıldı)", flush=True)
        else:
            if t <= a.devam:
                for pid in pidler:
                    islem(pid, False)
                duraklatildi = False
                print(f"[{damga}] {t} °C — soğudu, eğitim devam ediyor", flush=True)
        time.sleep(a.aralik)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBekçi kapatıldı; duraklatılmış süreç varsa devam ettiriliyor.")
        for pid in egitim_pidleri():
            islem(pid, False)
