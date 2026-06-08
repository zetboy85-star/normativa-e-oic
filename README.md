# Pacchetto portabile "normativa"

Questa cartella contiene tutto ciò che serve per usare la skill **normativa** da un ambiente diverso dal Mac originale (es. una sessione cloud raggiungibile dall'app Claude su telefono), **escluso** il corpus principale `italia-corpus` che è troppo grande (~70 GB) per essere copiato a mano ma è già un repo pubblico su GitHub.

## Cosa contiene

```
.claude/skills/normativa/SKILL.md   # skill riscritta con percorsi auto-rilevati (portabile)
OIC/                                 # corpus dei 29 principi contabili OIC (~22 MB, snapshot del 7/6/2026)
README.md                            # questo file
```

Peso totale: circa 3 MB — facilmente pubblicabile in un repository GitHub.

## Come attivare la skill in un ambiente remoto/cloud

1. **Pubblica questa cartella** in un tuo repository GitHub (può essere privato), ad es. `normativa-mobile`:
   ```bash
   cd "/Users/angelobasile/Desktop/Claude/Normativa-portable"
   git init
   git add .
   git commit -m "Pacchetto portabile skill normativa + corpus OIC"
   git remote add origin https://github.com/<tuo-utente>/normativa-mobile.git
   git push -u origin main
   ```

2. **Nell'ambiente cloud / sessione remota** (es. avviata dall'app Claude sul telefono), clona entrambi i repository nello stesso workspace:
   ```bash
   git clone https://github.com/<tuo-utente>/normativa-mobile.git
   # corpus principale: clone parziale consigliato vista la dimensione (~70 GB)
   git clone --filter=blob:none https://github.com/ahmeabd/italia-corpus.git
   ```
   Se lo spazio è limitato, valuta uno *sparse-checkout* per scaricare solo le cartelle/categorie che ti servono di più (es. `Codici`, `Decreti Legislativi`).

3. **Non serve modificare nulla**: la skill in `.claude/skills/normativa/SKILL.md` individua automaticamente, all'avvio, i percorsi di `italia-corpus` e `OIC/md` ovunque si trovino nel workspace (vedi il blocco "Prima di tutto: individua le cartelle del corpus" nella skill).

4. Da quel momento, dall'app sul telefono potrai fare le stesse domande che facciamo qui (es. "trovami le norme sulle holding", "riassumi il Codice della crisi d'impresa", "cosa dice l'OIC 16 sugli ammortamenti") e la skill funzionerà esattamente come in locale.

## Aggiornamenti

- `italia-corpus`: aggiornato regolarmente da terzi su GitHub — basta un `git pull` periodico nell'ambiente remoto.
- `OIC`: snapshot statico (7 giugno 2026). Per rigenerarlo da zero, vedi `OIC/convert.py` e `OIC/urls.txt` (script di conversione PDF → Markdown).
- La skill stessa: se la aggiorni in locale, ripeti il push del repo `normativa-mobile` e un `git pull` lato remoto.
