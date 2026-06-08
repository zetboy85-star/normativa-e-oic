#!/usr/bin/env python3
"""Converte i PDF dei principi OIC in Markdown semplice (estrazione testo per pagina)."""
import sys, re
from pathlib import Path
from pypdf import PdfReader

SRC = Path(__file__).parent / "pdf"
DST = Path(__file__).parent / "md"
DST.mkdir(exist_ok=True)

def clean(text: str) -> str:
    # normalizza spazi multipli e righe vuote eccessive, mantenendo la struttura
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

for pdf_path in sorted(SRC.glob("*.pdf")):
    out_path = DST / (pdf_path.stem + ".md")
    try:
        reader = PdfReader(str(pdf_path))
        title = pdf_path.stem.replace("-", " ")
        parts = [f"# {title}\n\n*Fonte: {pdf_path.name} (Fondazione OIC, fondazioneoic.eu)*\n"]
        for i, page in enumerate(reader.pages, start=1):
            txt = page.extract_text() or ""
            txt = clean(txt)
            if txt:
                parts.append(f"\n\n---\n\n## Pagina {i}\n\n{txt}")
        out_path.write_text("\n".join(parts), encoding="utf-8")
        print(f"OK  {pdf_path.name} -> {out_path.name} ({len(reader.pages)} pagine)")
    except Exception as e:
        print(f"ERR {pdf_path.name}: {e}", file=sys.stderr)
