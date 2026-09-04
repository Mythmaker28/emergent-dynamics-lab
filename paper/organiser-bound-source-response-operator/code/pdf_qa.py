"""Check rendered PDF text and bind the result to the exact PDF bytes (requires pypdf)."""
import re
from pypdf import PdfReader
from paths import PKG,PROV,digest,dump,require

def main():
    rows=[]
    for folder,stem in [('manuscript','MANUSCRIPT'),('supplement','SUPPLEMENT')]:
        p=PKG/folder/(stem+'.pdf'); reader=PdfReader(p)
        texts=[page.extract_text() or '' for page in reader.pages]
        require(all(len(s.strip())>80 for s in texts),'blank PDF page')
        text='\n'.join(texts)
        require('??' not in text and '\ufffd' not in text,'unresolved PDF glyph/reference')
        compact=re.sub(r'\s+','',text)  # Kerning in embedded Type-1 fonts can add spaces inside capitals.
        require('INDIVIDUATION:FAIL' in compact,'negative disposition absent from PDF')
        log=(PKG/folder/(stem+'.log')).read_text(encoding='utf-8',errors='replace')
        require('Overfull' not in log,'overflow in TeX log')
        require(not re.search(r'(?:Citation|Reference).*undefined',log),'undefined reference in TeX log')
        rows.append(dict(path=p.relative_to(PKG).as_posix(),sha256=digest(p),pages=len(reader.pages),
            text_characters=[len(s) for s in texts],overfull_boxes=0,
            underfull_warnings=log.count('Underfull')))
    dump(PROV/'PDF_QA.json',dict(status='PASS',checks='Extracted text, negative labels, no unresolved references or overfull boxes',files=rows))
    print('PDF text and log QA PASS:',[(r['path'],r['pages']) for r in rows])

if __name__=='__main__':main()
