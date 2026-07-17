#!/usr/bin/env python3
"""Render every PDF page and pair pages into lossless visual-QA sheets."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PDF_DIR = REPO / "output" / "pdf"
TMP = REPO / "tmp" / "pdfs"
PDFS = {
    "main": PDF_DIR / "PERSISTENCE_WITHOUT_OWNERSHIP_05.pdf",
    "supplement": PDF_DIR / "PERSISTENCE_WITHOUT_OWNERSHIP_05_SUPPLEMENT.pdf",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdftoppm", required=True, type=Path)
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()
    if args.cleanup:
        resolved = TMP.resolve()
        assert resolved == (REPO / "tmp" / "pdfs").resolve()
        if resolved.exists():
            shutil.rmtree(resolved)
        print(json.dumps({"cleaned": str(resolved)}))
        return

    assert args.pdftoppm.is_file(), args.pdftoppm
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    manifest = {"dpi": 140, "documents": {}}

    for label, pdf in PDFS.items():
        assert pdf.is_file(), pdf
        page_dir = TMP / label / "pages"
        sheet_dir = TMP / label / "sheets"
        page_dir.mkdir(parents=True)
        sheet_dir.mkdir(parents=True)
        subprocess.run(
            [str(args.pdftoppm), "-png", "-r", "140", str(pdf), str(page_dir / "page")],
            check=True,
        )
        pages = sorted(page_dir.glob("page-*.png"))
        assert pages
        sheets = []
        for offset in range(0, len(pages), 2):
            group = pages[offset : offset + 2]
            images = [Image.open(path).convert("RGB") for path in group]
            width = sum(image.width for image in images) + 30 * (len(images) + 1)
            height = max(image.height for image in images) + 80
            canvas = Image.new("RGB", (width, height), "#d8dde5")
            draw = ImageDraw.Draw(canvas)
            x = 30
            for page_no, (path, page_image) in enumerate(zip(group, images), start=offset + 1):
                draw.text((x, 12), f"{label} page {page_no}", fill="black")
                canvas.paste(page_image, (x, 45))
                x += page_image.width + 30
            sheet = sheet_dir / f"sheet-{offset // 2 + 1:02d}-pages-{offset + 1:02d}-{offset + len(group):02d}.png"
            canvas.save(sheet, optimize=True)
            sheets.append(sheet.relative_to(REPO).as_posix())
        manifest["documents"][label] = {
            "pages": len(pages),
            "rendered_pages": [path.relative_to(REPO).as_posix() for path in pages],
            "sheets": sheets,
        }

    (TMP / "qa_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
