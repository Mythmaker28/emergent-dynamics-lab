"""Build the V4.1 manuscript and supplement PDFs from their Markdown sources.

This is intentionally a small, deterministic renderer.  It does not execute
any scientific analysis and does not instantiate the simulation engine.
"""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "ORGANIZATIONAL_MEMORY_V4_1_RECONCILIATION.md"
SUPPLEMENT = ROOT / "SUPPLEMENT_V4_1.md"


def register_fonts() -> tuple[str, str, str]:
    windows_fonts = Path("C:/Windows/Fonts")
    candidates = [
        ("Arial", windows_fonts / "arial.ttf", windows_fonts / "arialbd.ttf", windows_fonts / "ariali.ttf"),
        ("DejaVuSans", Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf")),
    ]
    for family, regular, bold, italic in candidates:
        if regular.exists() and bold.exists() and italic.exists():
            pdfmetrics.registerFont(TTFont(family, str(regular)))
            pdfmetrics.registerFont(TTFont(f"{family}-Bold", str(bold)))
            pdfmetrics.registerFont(TTFont(f"{family}-Italic", str(italic)))
            pdfmetrics.registerFontFamily(
                family,
                normal=family,
                bold=f"{family}-Bold",
                italic=f"{family}-Italic",
                boldItalic=f"{family}-Bold",
            )
            return family, f"{family}-Bold", f"{family}-Italic"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


FONT, FONT_BOLD, FONT_ITALIC = register_fonts()


def styles():
    base = getSampleStyleSheet()
    ink = colors.HexColor("#1A2530")
    green = colors.HexColor("#14644D")
    muted = colors.HexColor("#58636D")
    return {
        "title": ParagraphStyle(
            "VTitle", parent=base["Title"], fontName=FONT_BOLD, fontSize=22,
            leading=26, textColor=ink, alignment=TA_LEFT, spaceAfter=8 * mm,
        ),
        "subtitle": ParagraphStyle(
            "VSubtitle", parent=base["Heading2"], fontName=FONT,
            fontSize=14, leading=18, textColor=green, spaceAfter=7 * mm,
        ),
        "h1": ParagraphStyle(
            "VH1", parent=base["Heading1"], fontName=FONT_BOLD, fontSize=14,
            leading=17, textColor=ink, spaceBefore=6 * mm, spaceAfter=2.5 * mm,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "VH2", parent=base["Heading2"], fontName=FONT_BOLD, fontSize=11.5,
            leading=14, textColor=green, spaceBefore=4 * mm, spaceAfter=1.8 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "VBody", parent=base["BodyText"], fontName=FONT, fontSize=9.1,
            leading=12.65, alignment=TA_JUSTIFY, textColor=ink,
            spaceAfter=2.2 * mm,
        ),
        "abstract": ParagraphStyle(
            "VAbstract", parent=base["BodyText"], fontName=FONT, fontSize=8.8,
            leading=12.15, alignment=TA_JUSTIFY, textColor=ink,
            leftIndent=7 * mm, rightIndent=7 * mm, spaceAfter=2.2 * mm,
        ),
        "caption": ParagraphStyle(
            "VCaption", parent=base["BodyText"], fontName=FONT, fontSize=8.0,
            leading=10.4, alignment=TA_LEFT, textColor=muted,
            leftIndent=3 * mm, rightIndent=3 * mm, spaceBefore=1.5 * mm,
            spaceAfter=4 * mm,
        ),
        "small": ParagraphStyle(
            "VSmall", parent=base["BodyText"], fontName=FONT, fontSize=8.0,
            leading=10.5, textColor=muted, spaceAfter=2 * mm,
        ),
        "bullet": ParagraphStyle(
            "VBullet", parent=base["BodyText"], fontName=FONT, fontSize=9.2,
            leading=12.6, textColor=ink, leftIndent=4 * mm,
        ),
        "table": ParagraphStyle(
            "VTable", parent=base["BodyText"], fontName=FONT, fontSize=7.4,
            leading=9.1, textColor=ink,
        ),
        "table_head": ParagraphStyle(
            "VTableHead", parent=base["BodyText"], fontName=FONT_BOLD,
            fontSize=7.4, leading=9.1, textColor=colors.white,
        ),
    }


STYLES = styles()


def inline_markup(text: str) -> str:
    text = escape(text.strip())
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


def paragraph(text: str, style: str = "body") -> Paragraph:
    return Paragraph(inline_markup(text), STYLES[style])


def parse_table(lines: list[str]) -> Table:
    rows: list[list[str]] = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", c or "") for c in cells):
            continue
        rows.append(cells)
    width = 170 * mm
    ncols = max(len(row) for row in rows)
    normalized = [row + [""] * (ncols - len(row)) for row in rows]
    weights = []
    for col in range(ncols):
        max_len = max(len(re.sub(r"`|\*|<[^>]+>", "", row[col])) for row in normalized)
        weights.append(max(7, min(max_len, 42)))
    total = sum(weights)
    col_widths = [width * w / total for w in weights]
    data = []
    for ridx, row in enumerate(normalized):
        style = "table_head" if ridx == 0 else "table"
        data.append([Paragraph(inline_markup(cell), STYLES[style]) for cell in row])
    table = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#315D66")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B9C4C7")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F2F6F5")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return table


def markdown_flowables(path: Path) -> list:
    lines = path.read_text(encoding="utf-8").splitlines()
    flow = []
    para_lines: list[str] = []
    bullet_lines: list[str] = []
    in_abstract = False

    def flush_para():
        nonlocal para_lines
        if para_lines:
            text = " ".join(line.strip() for line in para_lines)
            flow.append(paragraph(text, "abstract" if in_abstract else "body"))
            para_lines = []

    def flush_bullets():
        nonlocal bullet_lines
        if bullet_lines:
            items = [ListItem(paragraph(item, "bullet"), leftIndent=2 * mm)
                     for item in bullet_lines]
            flow.append(ListFlowable(
                items, bulletType="bullet", bulletFontName=FONT,
                bulletFontSize=7, leftIndent=8 * mm, bulletIndent=1.5 * mm,
                spaceAfter=2.5 * mm,
            ))
            bullet_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush_para()
            flush_bullets()
            i += 1
            continue
        if stripped == "<!-- PAGEBREAK -->":
            flush_para()
            flush_bullets()
            flow.append(PageBreak())
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
            flush_para()
            flush_bullets()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            flow.extend([Spacer(1, 1.5 * mm), parse_table(block), Spacer(1, 3 * mm)])
            continue
        image_match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            flush_para()
            flush_bullets()
            image_path = (path.parent / image_match.group(2)).resolve()
            img = Image(str(image_path))
            max_w, max_h = 170 * mm, 105 * mm
            scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
            img.drawWidth = img.imageWidth * scale
            img.drawHeight = img.imageHeight * scale
            img.hAlign = "CENTER"
            flow.extend([Spacer(1, 2 * mm), img])
            i += 1
            continue
        if stripped.startswith("# "):
            flush_para()
            flush_bullets()
            flow.append(Spacer(1, 12 * mm))
            flow.append(Paragraph(inline_markup(stripped[2:]), STYLES["title"]))
            flow.append(HRFlowable(
                width="100%", thickness=1.2, color=colors.HexColor("#14644D"),
                spaceAfter=5 * mm,
            ))
            i += 1
            continue
        if stripped.startswith("## "):
            flush_para()
            flush_bullets()
            heading = stripped[3:]
            if heading.startswith("Abstract"):
                in_abstract = True
            elif in_abstract:
                in_abstract = False
            style = "subtitle" if heading.startswith("A V4.1") else "h1"
            flow.append(Paragraph(inline_markup(heading), STYLES[style]))
            i += 1
            continue
        if stripped.startswith("### "):
            flush_para()
            flush_bullets()
            flow.append(Paragraph(inline_markup(stripped[4:]), STYLES["h2"]))
            i += 1
            continue
        if stripped.startswith("- "):
            flush_para()
            bullet_lines.append(stripped[2:])
            i += 1
            continue
        if stripped.startswith("*") and stripped.endswith("*") and len(stripped) > 2:
            flush_para()
            flush_bullets()
            flow.append(Paragraph(inline_markup(stripped[1:-1]), STYLES["caption"]))
            i += 1
            continue
        para_lines.append(stripped)
        i += 1

    flush_para()
    flush_bullets()
    return flow


def page_decor(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#B8C2C5"))
    canvas.setLineWidth(0.4)
    canvas.line(20 * mm, height - 14 * mm, width - 20 * mm, height - 14 * mm)
    canvas.setFont(FONT, 7.2)
    canvas.setFillColor(colors.HexColor("#66727A"))
    canvas.drawString(20 * mm, height - 11 * mm, "Organizational-memory V4.1 reconciliation")
    canvas.drawRightString(width - 20 * mm, 11 * mm, f"Page {doc.page}")
    canvas.drawString(20 * mm, 11 * mm, "No new simulations · canonical artifact reanalysis")
    canvas.restoreState()


def build(source: Path, output: Path, title: str):
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=19 * mm,
        bottomMargin=17 * mm,
        title=title,
        author="Tommy Lepesteur",
        subject="Original-world grouped reconciliation of committed V4 artifacts",
        keywords="grouped validation, leakage audit, reproducibility",
    )
    story = markdown_flowables(source)
    doc.build(story, onFirstPage=page_decor, onLaterPages=page_decor)


def main():
    jobs = [
        (
            MANUSCRIPT,
            ROOT / "ORGANIZATIONAL_MEMORY_V4_1_RECONCILIATION.pdf",
            "Organizational-memory claims under original-world grouped validation",
        ),
        (
            SUPPLEMENT,
            ROOT / "SUPPLEMENT_V4_1.pdf",
            "Supplement V4.1: original-world grouped statistical and artifact audit",
        ),
    ]
    for source, output, title in jobs:
        build(source, output, title)
        print(f"BUILT {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
