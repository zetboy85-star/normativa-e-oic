#!/usr/bin/env python3
"""Aggiornamento giornaliero del database normativo.

Due compiti indipendenti:
  1. digest delle modifiche di italia-corpus (atti nuovi, modificati, rimossi)
  2. controllo e aggiornamento dei principi contabili OIC da fondazioneoic.eu

Produce un file aggiornamenti/AAAA-MM-GG.md solo quando c'e' qualcosa da
riportare, per non lasciare un file vuoto al giorno nel repository.
"""
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORPUS_URL = "https://github.com/ahmeabd/italia-corpus.git"
OIC_DIR = REPO / "OIC"
MD_DIR = OIC_DIR / "md"
URLS_FILE = OIC_DIR / "urls.txt"
AGG_DIR = REPO / "aggiornamenti"
STATE_FILE = AGG_DIR / "stato.json"
# Le categorie del sito OIC sono annuali: si guarda l'anno scorso, questo e il prossimo.
CATEGORY_URL = "https://www.fondazioneoic.eu/principi-contabili-category/{anno}/"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def fetch(url, dest=None, timeout=120):
    """Scarica un URL con curl (rispetta il proxy e la CA bundle dell'ambiente)."""
    cmd = ["curl", "-sS", "--fail", "--max-time", str(timeout), "-L", url]
    if dest:
        cmd += ["-o", str(dest)]
        r = run(cmd)
        return r.returncode == 0
    r = run(cmd)
    return r.stdout if r.returncode == 0 else None


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


# --------------------------------------------------------------------------
# 1. digest italia-corpus
# --------------------------------------------------------------------------

def digest_corpus(state):
    """Clona i soli metadati git del corpus e riassume i commit non ancora visti."""
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "corpus"
        r = run(["git", "clone", "--filter=blob:none", "--no-checkout",
                 "--quiet", CORPUS_URL, str(clone)])
        if r.returncode != 0:
            return None, f"clone del corpus fallito: {r.stderr.strip()[:300]}"

        head = run(["git", "-C", str(clone), "rev-parse", "HEAD"]).stdout.strip()
        ultimo = state.get("ultimo_commit_corpus")
        if ultimo:
            intervallo = f"{ultimo}..HEAD"
            # Un commit salvato che il corpus non ha piu' (storia riscritta a monte).
            if run(["git", "-C", str(clone), "cat-file", "-e", ultimo + "^{commit}"]).returncode != 0:
                intervallo = None
        else:
            intervallo = None

        cmd = ["git", "-C", str(clone), "log", "--name-status",
               "--pretty=format:@@%H|%ad|%s", "--date=short"]
        cmd += [intervallo] if intervallo else ["--since=2 days ago"]
        out = run(cmd).stdout

        azioni = defaultdict(list)  # "A"/"M"/"D" -> [percorsi]
        commit = []
        for riga in out.splitlines():
            if riga.startswith("@@"):
                h, data, sogg = riga[2:].split("|", 2)
                commit.append((h[:8], data, sogg))
            elif riga and riga[0] in "AMD\t":
                parti = riga.split("\t")
                if len(parti) >= 2 and parti[0][:1] in "AMD":
                    azioni[parti[0][:1]].append(parti[-1])

        return {"head": head, "commit": commit, "azioni": azioni,
                "da_zero": intervallo is None}, None


def sezione_corpus(d):
    """Formatta il digest del corpus in markdown. Stringa vuota se nulla e' cambiato."""
    if not d or not d["commit"]:
        return ""
    righe = ["## Corpus normativo (italia-corpus)", ""]
    if d["da_zero"]:
        righe.append("*Prima esecuzione o storia a monte riscritta: "
                     "riportati i commit degli ultimi 2 giorni.*")
        righe.append("")
    righe.append(f"{len(d['commit'])} commit a monte "
                 f"(da {d['commit'][-1][1]} a {d['commit'][0][1]}).")
    righe.append("")

    etichette = [("A", "Atti nuovi"), ("M", "Atti modificati")]
    for chiave, titolo in etichette:
        percorsi = d["azioni"].get(chiave, [])
        if not percorsi:
            continue
        righe.append(f"### {titolo} ({len(percorsi)})")
        righe.append("")
        per_cat = defaultdict(list)
        for p in percorsi:
            per_cat[p.split("/")[0]].append(p.split("/")[-1])
        for cat in sorted(per_cat):
            voci = sorted(per_cat[cat])
            righe.append(f"**{cat}** — {len(voci)}")
            for v in voci[:15]:
                righe.append(f"- {v}")
            if len(voci) > 15:
                righe.append(f"- ...e altri {len(voci) - 15}")
            righe.append("")

    rimossi = d["azioni"].get("D", [])
    if rimossi:
        righe.append(f"### ATTENZIONE — atti rimossi a monte ({len(rimossi)})")
        righe.append("")
        righe.append("Una rimozione non corrisponde a un'abrogazione: di norma e' un "
                     "errore di manutenzione del corpus. Il testo resta recuperabile "
                     "dalla storia git (`git show <commit precedente>:\"<percorso>\"`).")
        righe.append("")
        for p in sorted(rimossi)[:30]:
            righe.append(f"- `{p}`")
        if len(rimossi) > 30:
            righe.append(f"- ...e altri {len(rimossi) - 30}")
        righe.append("")
    return "\n".join(righe)


# --------------------------------------------------------------------------
# 2. principi contabili OIC
# --------------------------------------------------------------------------

def url_noti():
    if not URLS_FILE.exists():
        return {}
    noti = {}
    for riga in URLS_FILE.read_text(encoding="utf-8").splitlines():
        parti = riga.split("|")
        if len(parti) == 3:
            noti[parti[2].strip()] = (parti[0].strip(), parti[1].strip())
    return noti


def url_pubblicati():
    """Tutti i PDF linkati dalle pagine-categoria OIC degli anni rilevanti."""
    anno = date.today().year
    trovati, errori = {}, []
    for a in (anno - 1, anno, anno + 1):
        html = fetch(CATEGORY_URL.format(anno=a), timeout=60)
        if html is None:
            # La categoria dell'anno prossimo spesso non esiste ancora: non e' un problema.
            if a <= anno:
                errori.append(str(a))
            continue
        for u in re.findall(r"https://[^\"'\s]+?\.pdf", html):
            trovati.setdefault(u, a)
    return trovati, errori


def numero_principio(url):
    m = re.search(r"OIC[-_ ]?(\d{1,2})\b", url, re.IGNORECASE)
    return int(m.group(1)) if m else None


def importa_pdfreader():
    """Prepara pypdf nell'interprete in esecuzione.

    Due trappole di questi container: `pip3` punta spesso a una versione di
    Python diversa da `python3`, e la `cryptography` di sistema puo' essere
    rotta in modo da far abortire l'import di pypdf con un panic nativo
    anziche' con un'eccezione. L'import si prova quindi in un sottoprocesso,
    cosi' un crash non abbatte il job, e si reinstalla cio' che manca.
    """
    prova = [sys.executable, "-I", "-c", "from pypdf import PdfReader"]
    if run(prova).returncode != 0:
        run([sys.executable, "-m", "pip", "install", "--quiet", "pypdf"])
        if run(prova).returncode != 0:
            # Una copia locale scavalca la cryptography di sistema difettosa.
            run([sys.executable, "-m", "pip", "install", "--quiet",
                 "--ignore-installed", "cryptography"])
    from pypdf import PdfReader
    return PdfReader


def converti_pdf(pdf_path, out_path):
    """Replica il formato di OIC/convert.py per un singolo PDF."""
    PdfReader = importa_pdfreader()

    def clean(t):
        t = re.sub(r"[ \t]+\n", "\n", t)
        return re.sub(r"\n{3,}", "\n\n", t).strip()

    reader = PdfReader(str(pdf_path))
    titolo = out_path.stem.replace("-", " ")
    parti = [f"# {titolo}\n\n*Fonte: {pdf_path.name} "
             f"(Fondazione OIC, fondazioneoic.eu)*\n"]
    for i, pagina in enumerate(reader.pages, start=1):
        txt = clean(pagina.extract_text() or "")
        if txt:
            parti.append(f"\n\n---\n\n## Pagina {i}\n\n{txt}")
    out_path.write_text("\n".join(parti), encoding="utf-8")
    return len(reader.pages)


def aggiorna_oic():
    noti = url_noti()
    pubblicati, errori = url_pubblicati()
    if not pubblicati:
        return "", [], ["nessuna pagina-categoria OIC raggiungibile "
                        f"(anni non letti: {', '.join(errori) or 'n/d'})"]

    nuovi = [u for u in pubblicati if u not in noti]
    if not nuovi:
        return "", [], [f"anni non letti: {', '.join(errori)}"] if errori else []

    righe = ["## Principi contabili OIC", "",
             f"{len(nuovi)} PDF non presenti nel corpus.", ""]
    modificati, problemi = [], []
    if errori:
        problemi.append(f"anni non letti: {', '.join(errori)}")

    with tempfile.TemporaryDirectory() as tmp:
        for u in sorted(nuovi, key=lambda x: (numero_principio(x) or 99, x)):
            n = numero_principio(u)
            if n is None:
                problemi.append(f"numero di principio non ricavabile da {u}")
                continue
            pdf = Path(tmp) / Path(u).name
            if not fetch(u, dest=pdf):
                problemi.append(f"download fallito: {u}")
                continue

            # Si riusa il nome del file markdown esistente per quel principio,
            # cosi' il corpus non cambia nomenclatura a ogni aggiornamento.
            esistenti = sorted(MD_DIR.glob(f"OIC-{n:02d}-*.md"))
            if esistenti:
                out = esistenti[0]
                stato = "aggiornato"
            else:
                slug = re.sub(r"^\d{4}(-\d{2})*-", "", pdf.stem)
                slug = re.sub(r"^OIC[-_ ]?\d{1,2}[-_ ]?", "", slug)
                out = MD_DIR / f"OIC-{n:02d}-{slug or 'principio'}.md"
                stato = "nuovo principio"
            try:
                pagine = converti_pdf(pdf, out)
            except Exception as e:  # pypdf assente o PDF illeggibile
                problemi.append(f"conversione fallita per OIC {n}: {e}")
                continue

            # urls.txt: si sostituisce la riga del principio, o se ne aggiunge una.
            titolo = out.stem.split("-", 2)[-1].replace("-", " ")
            righe_urls = URLS_FILE.read_text(encoding="utf-8").splitlines() if URLS_FILE.exists() else []
            sostituita = False
            for i, riga in enumerate(righe_urls):
                if riga.split("|")[0].strip() == str(n):
                    titolo = riga.split("|")[1].strip() or titolo
                    righe_urls[i] = f"{n}|{titolo}|{u}"
                    sostituita = True
                    break
            if not sostituita:
                righe_urls.append(f"{n}|{titolo}|{u}")
            righe_urls.sort(key=lambda r: int(r.split("|")[0]) if r.split("|")[0].strip().isdigit() else 99)
            URLS_FILE.write_text("\n".join(righe_urls) + "\n", encoding="utf-8")

            modificati.append(f"OIC {n}")
            righe.append(f"- **OIC {n} — {titolo}** ({stato}, {pagine} pagine) → "
                         f"`{out.relative_to(REPO)}`")
            righe.append(f"  - {u}")

    righe.append("")
    righe.append("I PDF non vengono committati: il corpus contiene solo il Markdown.")
    righe.append("")
    return "\n".join(righe), modificati, problemi


# --------------------------------------------------------------------------

def main():
    AGG_DIR.mkdir(exist_ok=True)
    oggi = date.today().isoformat()
    state = load_state()

    corpus, errore_corpus = digest_corpus(state)
    sez_corpus = sezione_corpus(corpus)
    sez_oic, oic_modificati, oic_problemi = aggiorna_oic()

    problemi = list(oic_problemi)
    if errore_corpus:
        problemi.append(errore_corpus)

    corpo = [p for p in (sez_corpus, sez_oic) if p]
    if not corpo and not problemi:
        print(f"{oggi}: nessuna novita'.")
        if corpus:
            state["ultimo_commit_corpus"] = corpus["head"]
            state["ultima_esecuzione"] = datetime.now().isoformat(timespec="seconds")
            STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        return 0

    testo = [f"# Aggiornamento database — {oggi}", ""]
    testo += corpo
    if problemi:
        testo += ["## Problemi riscontrati", ""]
        testo += [f"- {p}" for p in problemi] + [""]
    (AGG_DIR / f"{oggi}.md").write_text("\n".join(testo), encoding="utf-8")

    if corpus:
        state["ultimo_commit_corpus"] = corpus["head"]
    state["ultima_esecuzione"] = datetime.now().isoformat(timespec="seconds")
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    print(f"{oggi}: digest scritto.")
    print(f"  corpus: {len(corpus['commit']) if corpus else 0} commit")
    print(f"  OIC aggiornati: {', '.join(oic_modificati) or 'nessuno'}")
    for p in problemi:
        print(f"  problema: {p}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
