"""Resolve data-derived prose/tables and typeset the two PDFs with ReportLab.

Can run in a separate renderer interpreter: only reportlab and pypdf are needed.
DejaVu fonts and their license are included; no workstation lookup or network.
"""
from pathlib import Path
import hashlib
import html
import json
import re
from functools import partial
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
from reportlab.pdfgen import canvas
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = A4
MARGIN = 49
TEXTWIDTH = WIDTH - 2*MARGIN


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def mdtable(headers, rows):
    return "| " + " | ".join(headers) + " |\n|" + "|".join("---" for _ in headers) + "|\n" + "\n".join("| " + " | ".join(str(v) for v in row) + " |" for row in rows)


def substitutions():
    tokens = read(ROOT / "results/TEXT_VALUES.json")
    stats = read(ROOT / "results/SUMMARY.json")
    model = read(ROOT / "reviews/complex_systems/SOURCE_CHECK.json")
    refs = [r for r in read(ROOT / "reviews/complex_systems/VERIFIED_REFERENCES.json")["references"] if r["priority"] == "core"]
    assert len(refs) == 7
    refs.append({"authors":"Yoshua Bengio; Yves Grandvalet","title":"No Unbiased Estimator of the Variance of K-Fold Cross-Validation","journal":"Journal of Machine Learning Research","volume":"5","pages":"1089-1105","year":2004,"url":"https://www.jmlr.org/papers/v5/grandvalet04a.html"})
    tokens["REFERENCES"] = "\n\n".join(f"[{i}] {r['authors'].replace(';', ',')}. {r['title']}. {r['journal']} {r.get('volume','')}: {r.get('pages','')}, {r['year']}. " + ("https://doi.org/"+r["doi"] if r.get("doi") else r["url"]) for i,r in enumerate(refs,1))
    sensitivity=read(ROOT/"reviews/statistics/STATISTICAL_SENSITIVITY.json")
    # Counts come from the complete refitted deletion diagnostics.
    deletions=sensitivity["delete_one_full_refit"]
    tokens["N_REFIT"] = str(len(deletions))
    for scope in ["E","B","Gm"]:
        lower=[d["frozen_style_summaries"][scope]["lower"] for d in deletions]
        tokens["REFIT_PASS_"+scope.upper()] = str(sum(x>0 for x in lower))
        tokens["REFIT_FAIL_"+scope.upper()] = str(sum(x<=0 for x in lower))
    params=[]
    for group in ["scaffold_parameters", "memory_parameters"]:
        for key,val in model[group].items():
            params.append([group.replace("_parameters", ""),key,f"{val:g}"])
    tokens["PARAMETER_TABLE"] = mdtable(["Component", "Source parameter", "Value"], params)
    tokens["COHORT_TABLE"] = mdtable(["Stage / reason", "World count", "Interpretation"], [
        ["All primary worlds",stats["n_worlds"],"Denominator before any selection"],
        ["Initially ineligible",stats["feasibility"]["ineligible"],"Fewer than three eligible selected targets"],
        ["Split before deep",stats["feasibility"]["split"],"Tracking censor"],
        ["Lost before deep",stats["feasibility"]["lost"],"Tracking censor"],
        ["Deep reached and jointly valid",stats["n_valid"],"Conditional analysis population"]])
    names={"own":"Own target erasure", "own_minus_sham":"Own minus sham", "own_minus_neighbour":"Own minus neighbour", "fixed_within_branch":"Fixed within each branch", "plus_ablation_residual":"Uptake-channel ablation residual", "half_own_minus_residual":"Half own minus residual (post hoc)","full_ablation_residual":"Full readout ablation (diagnostic)"}
    tokens["CAUSAL_TABLE"] = mdtable(["World contrast", "Mean", "World-level 95% t interval", "Positive worlds"], [[names[k],f"{v['mean']:.6f}",f"[{v['lower']:.6f}, {v['upper']:.6f}]",v['n_positive']] for k,v in stats['causal'].items()])
    (ROOT / "results/RESOLVED_VALUES.json").write_text(json.dumps(tokens,indent=2)+"\n",encoding="utf-8",newline="\n")
    return tokens


def fonts():
    # Initial Vera build lacked rho/lambda; visual review caught this defect.
    # Included DejaVu covers Greek; verify bytes and glyph coverage below.
    base=ROOT / "assets/fonts"
    for row in read(base/"MANIFEST.json")["files"]:
        content=(base/row["path"]).read_bytes()
        assert len(content)==row["bytes"] and hashlib.sha256(content).hexdigest()==row["sha256"]
    for name,filename in [("Body","DejaVuSerif.ttf"),("Body-Bold","DejaVuSerif-Bold.ttf"),("Body-Italic","DejaVuSerif-Italic.ttf"),("Body-BoldItalic","DejaVuSerif-BoldItalic.ttf")]:
        pdfmetrics.registerFont(TTFont(name,str(base/filename)))
    pdfmetrics.registerFontFamily("Body",normal="Body",bold="Body-Bold",italic="Body-Italic",boldItalic="Body-BoldItalic")


def rich(text):
    text=html.escape(text)
    sub=dict(zip("₀₁₂₃₄₅₆₇₈₉₊₋ₖᵢⱼₛ", "0123456789+-kijs"))
    sup={"ᶠ":"f", "ᵂ":"w", "ᵂ":"w", "ᵂ":"w", "⁻":"-", "⁴":"4", "¹":"1", "²":"2", "⁺":"+"}
    text="".join(f"<sub>{sub[c]}</sub>" if c in sub else f"<super>{sup[c]}</super>" if c in sup else c for c in text)
    # Plain-text equivalents keep discrete updates readable in PDF extraction.
    for a,b in [("⊕"," concatenated with "),("←"," &lt;- "),("→"," -&gt; "),("−","-"),("≤","&lt;="),("≥","&gt;="),("≠","!=")]: text=text.replace(a,b)
    text=re.sub(r"`([^`]+)`",r'<font name="Courier" size="8">\1</font>',text)
    text=re.sub(r"\*\*([^*]+)\*\*",r"<b>\1</b>",text)
    text=re.sub(r"\*([^*]+)\*",r"<i>\1</i>",text)
    text=re.sub(r"https?://[^\s<]+",lambda m:'<link href="'+m.group(0)+'" color="#21618C">'+m.group(0)+'</link>',text)
    return text


def render(md, path, supplement=False):
    plain=html.unescape(re.sub(r"<[^>]*>","",rich(md)))
    for font in ["Body","Body-Bold","Body-Italic","Body-BoldItalic"]:
        chars=pdfmetrics.getFont(font).face.charWidths
        missing=sorted({c for c in plain if not c.isspace() and ord(c) not in chars})
        assert not missing,(font,"missing glyphs",missing)
    styles={
        "body":ParagraphStyle("body",fontName="Body",fontSize=9.35,leading=13.3,spaceAfter=7,alignment=TA_JUSTIFY,splitLongWords=True),
        "title":ParagraphStyle("title",fontName="Body-Bold",fontSize=20,leading=24,spaceAfter=15,textColor=colors.HexColor("#163C55")),
        "h2":ParagraphStyle("h2",fontName="Body-Bold",fontSize=12.2,leading=16,spaceBefore=13,spaceAfter=7,keepWithNext=True,textColor=colors.HexColor("#163C55")),
        "h3":ParagraphStyle("h3",fontName="Body-Bold",fontSize=10,leading=14,spaceBefore=9,spaceAfter=5,keepWithNext=True),
        "caption":ParagraphStyle("caption",fontName="Body",fontSize=8.1,leading=11.4,spaceAfter=10,alignment=TA_LEFT),
        "table":ParagraphStyle("table",fontName="Body",fontSize=7.7,leading=10.3,spaceAfter=0),
        "equation":ParagraphStyle("equation",fontName="Body",fontSize=8.7,leading=13,spaceAfter=4,leftIndent=12,rightIndent=12),
        "reference":ParagraphStyle("reference",fontName="Body",fontSize=8,leading=11.2,spaceAfter=6,alignment=TA_LEFT)
    }
    lines=md.splitlines();story=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1;continue
        if line.startswith("!["):
            match=re.fullmatch(r"!\[([^]]+)\]\(([^)]+)\)",line);assert match,line
            imgpath=ROOT/match[2]; w,h=ImageReader(str(imgpath)).getSize(); scale=min(TEXTWIDTH/w,250/h)
            block=[Image(str(imgpath),width=w*scale,height=h*scale),Spacer(1,5)]
            j=i+1
            while j<len(lines) and not lines[j].strip():j+=1
            if j<len(lines) and lines[j].startswith("*Figure"):
                block.append(Paragraph(rich(lines[j]),styles["caption"]));i=j
            story.append(KeepTogether(block));i+=1;continue
        if line.startswith("|"):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith("|"):
                cells=[x.strip() for x in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?",c) for c in cells):rows.append(cells)
                i+=1
            ncols=len(rows[0]);assert all(len(r)==ncols for r in rows)
            if ncols==3: widths=[TEXTWIDTH*.43,TEXTWIDTH*.24,TEXTWIDTH*.33]
            elif ncols==4 and rows[0][0]=="Scope":widths=[TEXTWIDTH*.08,TEXTWIDTH*.57,TEXTWIDTH*.12,TEXTWIDTH*.23]
            elif ncols==4:widths=[TEXTWIDTH*.40,TEXTWIDTH*.12,TEXTWIDTH*.34,TEXTWIDTH*.14]
            else:widths=[TEXTWIDTH/ncols]*ncols
            table=Table([[Paragraph(rich(c),styles["table"]) for c in row] for row in rows],colWidths=widths,repeatRows=1,hAlign="LEFT")
            table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#DFEAF0")),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F5F7F8")]),("LINEBELOW",(0,0),(-1,0),.6,colors.HexColor("#A1B4BF")),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
            story.extend([table,Spacer(1,8)]);continue
        if line.startswith("### "): story.append(Paragraph(rich(line[4:]),styles["h3"]))
        elif line.startswith("## "): story.append(Paragraph(rich(line[3:]),styles["h2"]))
        elif line.startswith("# "): story.append(Paragraph(rich(line[2:]),styles["title"]))
        elif line.startswith(">"):
            if line[1:].strip():story.append(Paragraph(rich(line[1:].strip()),styles["equation"]))
        else:
            if re.match(r"\[\d+\]",line):sty=styles["reference"]
            elif line.startswith("*Table"):sty=styles["caption"]
            else:sty=styles["body"]
            story.append(Paragraph(rich(line),sty))
        i+=1
    title=md.splitlines()[0].removeprefix("# ")
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=MARGIN,leftMargin=MARGIN,topMargin=46,bottomMargin=46,title=title,author="Tommy Lepesteur",pageCompression=1,invariant=1)
    def page(c,d):
        c.saveState();c.setStrokeColor(colors.HexColor("#C8D3DA"));c.setLineWidth(.4);c.line(MARGIN,HEIGHT-29,WIDTH-MARGIN,HEIGHT-29)
        c.setFont("Body",7);c.setFillColor(colors.HexColor("#536575"))
        c.drawString(MARGIN,HEIGHT-22,"SUPPLEMENT" if supplement else "TESTING CAUSAL MEMORY EXPRESSION AND LOCAL PREDICTIVE ADVANTAGE")
        c.drawString(MARGIN,25,"Author review version • 5 September 2026")
        c.drawRightString(WIDTH-MARGIN,25,str(d.page));c.restoreState()
    doc.build(story,onFirstPage=page,onLaterPages=page,canvasmaker=partial(canvas.Canvas,invariant=1))
    reader=PdfReader(path); text="\n".join(p.extract_text() for p in reader.pages)
    assert "{{" not in text
    assert all(p.extract_text().strip() for p in reader.pages)
    return {"path":path.name,"pages":len(reader.pages),"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"characters_extracted":len(text)}


def main():
    fonts();tokens=substitutions();outputs=[]
    for stem in ["MANUSCRIPT","SUPPLEMENT"]:
        text=(ROOT/(stem+".md")).read_text(encoding="utf-8")
        keys=re.findall(r"\{\{([A-Z_]+)\}\}",text)
        assert all(k in tokens for k in keys),[k for k in keys if k not in tokens]
        text=re.sub(r"\{\{([A-Z_]+)\}\}",lambda m:tokens[m[1]],text)
        assert "{{" not in text
        (ROOT/(stem+"_RESOLVED.md")).write_text(text,encoding="utf-8",newline="\n")
        outputs.append(render(text,ROOT/(stem+".pdf"),stem=="SUPPLEMENT"))
    (ROOT/"results/PDF_BUILD.json").write_text(json.dumps({"renderer":"ReportLab "+reportlab.Version,"outputs":outputs},indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(outputs))


if __name__ == "__main__":main()
