"""Render every V4.1 PDF page and create contact sheets for visual QA."""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
POPPLER = Path(
    "C:/Users/tommy/.cache/codex-runtimes/codex-primary-runtime/"
    "dependencies/native/poppler/Library/bin/pdftoppm.exe"
)
PDFS = [
    ROOT / "ORGANIZATIONAL_MEMORY_V4_1_RECONCILIATION.pdf",
    ROOT / "SUPPLEMENT_V4_1.pdf",
    ROOT.parent / "v4.0" / "canonical" / "docs" / "paper" / "full"
    / "ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V4.pdf",
    ROOT.parent / "v4.0" / "canonical" / "docs" / "paper" / "full"
    / "SUPPLEMENT_V4.pdf",
]


def render(pdf: Path) -> tuple[list[Path], Path]:
    out_dir = ROOT / "qa_render" / pdf.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    for old_page in out_dir.glob("page-*.png"):
        old_page.unlink()
    prefix = out_dir / "page"
    subprocess.run(
        [str(POPPLER), "-png", "-r", "130", str(pdf), str(prefix)],
        check=True,
    )
    pages = sorted(out_dir.glob("page-*.png"))
    thumbs = []
    for page in pages:
        with Image.open(page) as im:
            thumb = im.convert("RGB")
            thumb.thumbnail((380, 540))
            thumbs.append((page.name, thumb.copy()))
    cols = 3
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 410, rows * 580), "white")
    draw = ImageDraw.Draw(sheet)
    for idx, (name, thumb) in enumerate(thumbs):
        x = (idx % cols) * 410 + 15
        y = (idx // cols) * 580 + 28
        sheet.paste(thumb, (x, y))
        draw.text((x, 7 + (idx // cols) * 580), name, fill="#263238")
    contact = ROOT / "qa_render" / f"{pdf.stem}_contact_sheet.png"
    contact.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(contact)
    return pages, contact


def main():
    for pdf in PDFS:
        pages, contact = render(pdf)
        print(f"RENDERED {pdf.name}: {len(pages)} pages")
        print(f"CONTACT {contact}")


if __name__ == "__main__":
    main()
