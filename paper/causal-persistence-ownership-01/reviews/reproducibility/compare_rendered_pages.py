"""Bind the final PDF render to every individually inspected page image."""
from pathlib import Path
import argparse
import hashlib
import json


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--inspected",required=True);ap.add_argument("--final",required=True);args=ap.parse_args()
    inspected=Path(args.inspected);final=Path(args.final);rows=[]
    for stem,count in [("manuscript",8),("supplement",9)]:
        for n in range(1,count+1):
            name=f"{stem}-page-{n}.png"
            a=(inspected/name).read_bytes();b=(final/name).read_bytes()
            rows.append({"document":stem,"page":n,"inspected_png_sha256":hashlib.sha256(a).hexdigest(),"final_png_sha256":hashlib.sha256(b).hexdigest(),"byte_identical":a==b})
    result={"status":"PASS" if all(r["byte_identical"] for r in rows) else "FAIL","scope":"Each page was individually visually inspected in round 2. All final PDFs were rendered again at the identical Poppler settings; this compares every final PNG with its inspected counterpart.","render_command":"pdftoppm -r 75 -png DOCUMENT.pdf PREFIX","pages":rows}
    (Path(__file__).resolve().parent/"FINAL_VISUAL_CHECK.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":result["status"],"pages":len(rows),"all_byte_identical":all(r["byte_identical"] for r in rows)}))


if __name__=="__main__":main()
