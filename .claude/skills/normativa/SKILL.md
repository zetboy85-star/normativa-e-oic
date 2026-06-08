---
name: normativa
description: Cerca, riassume, confronta e spiega leggi, decreti, regolamenti, codici, atti normativi italiani e principi contabili nazionali OIC usando i corpus "italia-corpus" (oltre 250.000 atti in Markdown clonati da Normattiva) e "OIC" (i 29 principi contabili nazionali emanati dalla Fondazione OIC, anch'essi in Markdown). Usa SEMPRE questa skill quando l'utente fa domande sulla legislazione italiana o sui principi contabili OIC, chiede di trovare una legge/decreto/DPR/DPCM/codice/principio contabile su un certo argomento, vuole un riassunto o una spiegazione di un atto normativo o di un OIC specifico, vuole sapere cosa dice la legge o un principio contabile su un tema, oppure vuole confrontare versioni storiche di una norma — anche se non nomina esplicitamente "normativa", "italia-corpus", "OIC" o "Markdown".
---

# Normativa: esplorare il corpus della legislazione italiana

## Prima di tutto: individua le cartelle del corpus

Questa skill è **portabile**: non assume un percorso fisso. I corpus (`italia-corpus` e `OIC`) si trovano da qualche parte nel progetto/workspace corrente, di solito accanto alla cartella `.claude` da cui è caricata questa skill (la "base directory" indicata all'avvio della skill).

Prima di qualunque ricerca, individua i percorsi con un comando come questo (adatta la profondità/il punto di partenza al tuo ambiente):

```bash
# cerca a partire dalla home o dalla root del progetto/workspace
ITALIA_CORPUS="$(find ~ -maxdepth 6 -type d -name "italia-corpus" 2>/dev/null | head -1)"
OIC_DIR="$(find ~ -maxdepth 6 -type d -path "*OIC/md" 2>/dev/null | head -1)"
echo "italia-corpus: $ITALIA_CORPUS"
echo "OIC/md:        $OIC_DIR"
```

Se l'ambiente è un workspace cloud clonato da repository git, i due corpus potrebbero essere in repo separati (vedi sezione "Setup in ambienti remoti/cloud" più sotto) — in tal caso individua le rispettive cartelle nel workspace.

Usa sempre le variabili `$ITALIA_CORPUS` e `$OIC_DIR` (o i percorsi assoluti che hai trovato) nei comandi seguenti, al posto di percorsi fissi.

## Cos'è il corpus italia-corpus

`$ITALIA_CORPUS` è un repo git con oltre 250.000 atti normativi italiani (fonte: Normattiva), uno per file `.md`, organizzati in ~23 cartelle per categoria. Esempi di cartelle: `Codici`, `DPR`, `DPCM`, `Decreti Legislativi`, `Leggi costituzionali`, `Regi decreti`, `Atti di attuazione Regolamenti UE`, `Atti di recepimento direttive UE`, `Atti normativi abrogati (in originale)`, `DL e leggi di conversione`, `Leggi di ratifica`, `Leggi finanziarie e di bilancio`, ecc.

Ogni file `.md` contiene il testo di un singolo atto: legge, decreto legislativo, DPR, regolamento... Il nome del file è quasi sempre il titolo (o un estratto del titolo) dell'atto, il che lo rende un buon punto di partenza per la ricerca.

Essendo un repo git, ogni aggiornamento legislativo corrisponde a un commit: questo permette di vedere come un atto è cambiato nel tempo.

> Nota dimensione: il repo `italia-corpus` pesa circa **70 GB**. Se lavori in un ambiente con spazio limitato, valuta un clone parziale (`git clone --filter=blob:none` / sparse-checkout sulle sole categorie che ti servono) invece di un clone completo.

## Perché serve una strategia di ricerca mirata

Con 250.000+ file, leggere o elencare tutto è impossibile e inutile. La chiave è restringere il campo il più possibile prima di aprire qualunque file: prima cerca per nome (più veloce, più mirato), poi eventualmente per contenuto solo nelle cartelle/sotto-insiemi rilevanti, e apri solo i file che sembrano davvero pertinenti.

## Strategie pratiche

**1. Cerca per nome file quando conosci (anche vagamente) il titolo o l'argomento:**

```bash
find "$ITALIA_CORPUS" -iname "*ecolabel*"
find "$ITALIA_CORPUS/Codici" -iname "*privacy*"
```

**2. Cerca nel contenuto quando il termine non compare nel titolo, o vuoi capire dove un argomento è trattato.** Usa `grep -ril` (case-insensitive, solo nomi file) per restare leggero, poi approfondisci con `grep -n` sui file che contano:

```bash
# trova in quali atti si parla di un certo argomento (solo elenco file)
grep -ril "ecobonus" "$ITALIA_CORPUS" --include="*.md"

# se vuoi restringere a una categoria
grep -ril "intelligenza artificiale" "$ITALIA_CORPUS/Decreti Legislativi" --include="*.md"

# poi, su un file specifico, trova le righe/articoli pertinenti con contesto
grep -n -B1 -A3 "intelligenza artificiale" "<percorso del file trovato>"
```

Se una ricerca ampia restituisce troppi risultati, raffina i termini (sinonimi, forme giuridiche tipiche come "disposizioni in materia di...", riferimenti normativi, anni) o aggiungi un filtro di cartella/categoria pertinente.

**3. Per riassumere o spiegare un atto specifico:** individua il file corretto (di solito basta `find -iname`), poi leggine il contenuto e produci una sintesi in linguaggio chiaro — articoli principali, ambito di applicazione, eventuali modifiche ad altre norme. Indica sempre il nome del file/atto da cui proviene la sintesi.

**4. Per esplorare la struttura del corpus o capire dove cercare:** elenca le cartelle di primo livello e, se utile, conta i file in una categoria:

```bash
ls "$ITALIA_CORPUS"
find "$ITALIA_CORPUS/Codici" -maxdepth 1 -name "*.md" | wc -l
```

**5. Per vedere la storia/le modifiche di un atto nel tempo:** sfrutta git, dato che ogni aggiornamento legislativo è un commit:

```bash
cd "$ITALIA_CORPUS"
git log --follow --oneline -- "<percorso del file>"
git log -p --follow -- "<percorso del file>"   # per vedere anche le modifiche riga per riga
git show <hash_commit>:"<percorso del file>"   # contenuto dell'atto a una data versione
```

Questo è utile per domande tipo "come è cambiata questa norma nel tempo?" o "cosa diceva questo articolo prima della modifica del 2023?".

> In un clone parziale/superficiale la storia potrebbe non essere completa: se `git log` restituisce poco, segnalalo all'utente e suggerisci eventualmente un `git fetch --unshallow`.

## Citare sempre la fonte

Ogni risposta basata sul corpus deve indicare chiaramente da quale atto proviene l'informazione: nome del file (che di solito coincide con il titolo dell'atto) e, quando possibile, l'articolo o la sezione specifica. Questo è essenziale perché l'utente possa verificare l'informazione e perché il corpus stesso serve proprio a rendere la legislazione tracciabile e verificabile — un riassunto o una risposta senza riferimento alla fonte vanifica lo scopo della ricerca.

Esempio di formato di citazione: *"Secondo il DPR 'Regolamento recante norme per la semplificazione...' (file: `DPR/Regolamento recante norme per la semplificazione....md`), l'art. 3 stabilisce che..."*

## Il corpus dei principi contabili OIC

Oltre a `italia-corpus`, è disponibile anche una raccolta dei **principi contabili nazionali OIC** (Organismo Italiano di Contabilità), in `$OIC_DIR` (tipicamente `OIC/md` nel workspace).

29 file Markdown, uno per principio (es. `OIC-11-Postulati.md`, `OIC-16-Immobilizzazioni-materiali.md`, `OIC-25-Imposte-sul-reddito.md`...). A differenza degli atti di `italia-corpus`, questi non sono leggi ma documenti tecnici di standard-setting contabile emanati dalla Fondazione OIC (fondazioneoic.eu) — utili per domande su bilancio d'esercizio, criteri di valutazione contabile, schemi di bilancio, rilevazione di crediti/debiti/immobilizzazioni/rimanenze, ecc.

Vedi `OIC/README.md` (nella cartella padre di `$OIC_DIR`) per l'elenco completo con la mappatura numero → titolo → file. Per cercare un argomento al loro interno, usa la stessa logica grep vista sopra:

```bash
grep -ril "ammortamento" "$OIC_DIR"
grep -n -B1 -A3 "rilevanza" "$OIC_DIR/OIC-11-Postulati.md"
```

Nota: questa raccolta è uno **snapshot statico** (scaricato il 7 giugno 2026, non si aggiorna automaticamente come `italia-corpus`). Se la domanda riguarda l'ultimissima versione di un principio o emendamenti recentissimi, segnalalo all'utente e suggerisci di verificare su fondazioneoic.eu.

## Nota sui duplicati di nome (maiuscole/minuscole)

Su filesystem case-insensitive (come macOS/APFS di default, ma non necessariamente in ambienti cloud Linux) può capitare che due atti con nomi che differiscono solo per maiuscole/minuscole risultino sovrapposti sul disco, anche se nel repo git sono file distinti. Se una ricerca per nome restituisce un solo file ma il contenuto sembra non corrispondere a quanto ti aspetti, prova a verificare nel repo git con `git ls-tree -r --name-only HEAD -- "<cartella>"` se esistono varianti con maiuscole diverse, e usa `git show HEAD:"<percorso esatto dal repo>"` per leggere il contenuto corretto direttamente dall'indice git.

## Setup in ambienti remoti/cloud (es. per usare la skill da telefono)

Per rendere questa skill disponibile da un ambiente diverso dal Mac originale (es. una sessione cloud raggiungibile dall'app mobile):

1. **`italia-corpus`** è già un repo pubblico: `https://github.com/ahmeabd/italia-corpus.git`. In un ambiente cloud puoi clonarlo (idealmente con `--filter=blob:none` o sparse-checkout, vista la dimensione di ~70 GB) invece di trasferirlo manualmente.
2. **`OIC`** (~22 MB) e questa **cartella `.claude/skills/normativa`** (pochi KB) vanno invece pubblicati/copiati a parte — ad es. in un piccolo repo dedicato — perché non fanno parte del repo `italia-corpus` originale.
3. Una volta che entrambi i corpus sono presenti nel workspace cloud (in qualunque punto della struttura), questa skill li individua automaticamente tramite il comando `find` mostrato all'inizio: non servono modifiche ai percorsi.
