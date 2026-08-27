"""
make_thumbnails.py
-------------------
สคริปต์นี้จะสร้างรูปพรีวิวขนาดเล็ก (ไม่เกิน 1000x1000 px) จากรูปเต็มในโฟลเดอร์ Img/
แล้วบันทึกไว้ในโฟลเดอร์ Img/THUMB/ โดยคงโครงสร้างโฟลเดอร์เดิมไว้ทุกอย่าง
เว็บไซต์ (index.html) จะโหลดรูปจาก Img/THUMB/ ให้อัตโนมัติสำหรับหน้ารายการสินค้า
ส่วนรูปเต็มจะโหลดเฉพาะตอนลูกค้ากด "ดูรายละเอียด" เท่านั้น

วิธีใช้งาน:
1. ติดตั้ง Pillow ก่อน (ครั้งเดียว):
      pip install Pillow

2. วางไฟล์นี้ไว้ในโฟลเดอร์เดียวกับ index.html (โฟลเดอร์ที่มีโฟลเดอร์ Img/ อยู่ข้างใน)

3. รันคำสั่ง:
      python make_thumbnails.py

4. สคริปต์จะสร้างโฟลเดอร์ Img/THUMB/... ให้เองพร้อมรูปย่อทั้งหมด
   รันซ้ำได้เรื่อยๆ เวลาเพิ่มรูปสินค้าใหม่ (จะข้ามไฟล์ที่มี thumbnail อยู่แล้วและไม่เก่ากว่ารูปต้นฉบับ)
"""

import os
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise SystemExit("ยังไม่ได้ติดตั้ง Pillow กรุณารันคำสั่ง: pip install Pillow")

SRC_ROOT = Path("Img")
DST_ROOT = Path("Img") / "THUMB"
MAX_SIZE = (1000, 1000)
JPEG_QUALITY = 82
SKIP_DIRS = {"THUMB", "Icon", "LOGO"}          # ไม่ต้องย่อไอคอน/โลโก้ (ไฟล์เล็กอยู่แล้ว)
VALID_EXT = {".jpg", ".jpeg", ".png", ".webp"}


def should_skip_dir(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def make_thumbnail(src_path: Path, dst_path: Path):
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    # ข้ามไฟล์ที่มี thumbnail อยู่แล้วและยังใหม่กว่ารูปต้นฉบับ
    if dst_path.exists() and dst_path.stat().st_mtime >= src_path.stat().st_mtime:
        return "skip"

    with Image.open(src_path) as im:
        im = im.convert("RGB") if im.mode in ("P", "RGBA") and dst_path.suffix.lower() in (".jpg", ".jpeg") else im
        im.thumbnail(MAX_SIZE, Image.LANCZOS)

        save_kwargs = {}
        ext = dst_path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            if im.mode != "RGB":
                im = im.convert("RGB")
            save_kwargs = dict(quality=JPEG_QUALITY, optimize=True, progressive=True)
        elif ext == ".png":
            save_kwargs = dict(optimize=True)
        elif ext == ".webp":
            save_kwargs = dict(quality=JPEG_QUALITY, method=6)

        im.save(dst_path, **save_kwargs)
    return "ok"


def main():
    if not SRC_ROOT.exists():
        raise SystemExit(f"ไม่พบโฟลเดอร์ {SRC_ROOT}/ กรุณารันสคริปต์นี้ในโฟลเดอร์เดียวกับ index.html")

    created, skipped, failed = 0, 0, 0

    for src_path in SRC_ROOT.rglob("*"):
        if not src_path.is_file():
            continue
        if src_path.suffix.lower() not in VALID_EXT:
            continue
        rel = src_path.relative_to(SRC_ROOT)
        if should_skip_dir(rel):
            continue

        dst_path = DST_ROOT / rel
        try:
            result = make_thumbnail(src_path, dst_path)
            if result == "ok":
                created += 1
                print(f"✓ {rel}")
            else:
                skipped += 1
        except Exception as e:
            failed += 1
            print(f"✗ ผิดพลาด: {rel} -> {e}")

    print("\n----------------------------------")
    print(f"สร้างใหม่: {created} ไฟล์")
    print(f"ข้าม (มีอยู่แล้ว): {skipped} ไฟล์")
    print(f"ผิดพลาด: {failed} ไฟล์")
    print("----------------------------------")


if __name__ == "__main__":
    main()
