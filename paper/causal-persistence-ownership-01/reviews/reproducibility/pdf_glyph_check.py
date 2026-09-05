"""Independent static font coverage and PDF extraction check, without rendering.

Visual page inspection is separately required. This does not claim that text
extraction proves visual correctness.
"""
from pathlib import Path
import argparse
import hashlib
import html
import importlib.util
import json
import re
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--paper",required=True);args=ap.parse_args()
    paper=Path(args.paper).resolve()
    font_manifest=json.loads((paper/"assets/fonts/MANIFEST.json").read_text(encoding="utf-8"))
    assets=[]
    for item in font_manifest["files"]:
        p=(paper/"assets/fonts"/item["path"]).resolve()
        assert p.is_relative_to((paper/"assets/fonts").resolve())
        content=p.read_bytes();digest=hashlib.sha256(content).hexdigest()
        assert len(content)==item["bytes"] and digest==item["sha256"]
        assets.append({"path":item["path"],"bytes":len(content),"sha256":digest,"manifest_match":True})
    spec=importlib.util.spec_from_file_location("reviewed_document_builder",paper/"scripts/build_documents.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.fonts()
    docs=[]
    for stem in ["MANUSCRIPT","SUPPLEMENT"]:
        raw=(paper/(stem+"_RESOLVED.md")).read_text(encoding="utf-8")
        text=html.unescape(re.sub("<[^>]+>","",mod.rich(raw)))
        chars={ord(c) for c in text if c.isprintable()}
        missing={name:[f"U+{c:04X}" for c in sorted(chars) if c not in pdfmetrics.getFont(name).face.charToGlyph] for name in ["Body","Body-Bold","Body-Italic","Body-BoldItalic"]}
        p=paper/(stem+".pdf");reader=PdfReader(p)
        pdf_fonts={}
        page_texts=[]
        for page in reader.pages:
            page_texts.append(page.extract_text())
            for _,ref in page["/Resources"].get("/Font",{}).items():
                font=ref.get_object();name=str(font.get("/BaseFont"))
                descriptor=font.get("/FontDescriptor")
                pdf_fonts[name]={"subtype":str(font.get("/Subtype")),"has_embedded_font":bool(descriptor and any(k in descriptor.get_object() for k in ["/FontFile","/FontFile2","/FontFile3"]))}
        docs.append({"document":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"pages":len(reader.pages),"missing_codepoints_in_body_faces":missing,"empty_pages":[i+1 for i,t in enumerate(page_texts) if not t.strip()],"unresolved_tokens":any("{{" in t for t in page_texts),"fonts":pdf_fonts})
    result={"status":"PASS" if all(not any(d["missing_codepoints_in_body_faces"].values()) and not d["empty_pages"] and not d["unresolved_tokens"] for d in docs) else "FAIL","scope":"Static used-body-glyph coverage, PDF embedding and extraction; visual inspection documented separately.","font_assets_verified":assets,"documents":docs}
    dest=Path(__file__).resolve().parent/"PDF_GLYPH_CHECK.json"
    dest.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
