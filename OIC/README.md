# Principi Contabili Nazionali OIC

Raccolta locale dei **principi contabili nazionali** emanati dall'Organismo Italiano di Contabilità (OIC), scaricati dal sito ufficiale della Fondazione OIC ([fondazioneoic.eu](https://www.fondazioneoic.eu)) e convertiti in Markdown per la consultazione e la ricerca testuale.

> Nota: a differenza del corpus `italia-corpus` (legislazione pubblicata su Normattiva), gli OIC **non sono atti legislativi** ma documenti tecnici di un ente di standard-setting privato. Questa cartella è mantenuta separata per evitare conflitti con gli aggiornamenti automatici di `italia-corpus`.

## Struttura

- `pdf/` — documenti originali in PDF, scaricati da fondazioneoic.eu
- `md/` — versione convertita in Markdown (un file per principio, paginato)
- `convert.py` — script di conversione PDF → Markdown (usa `pypdf`)
- `urls.txt` — elenco sorgente: numero | titolo | URL del PDF originale

## Elenco principi inclusi (29, versioni in vigore al 7 giugno 2026)

| N. | Titolo | File Markdown |
|----|--------|---------------|
| OIC 2 | Patrimoni destinati | `md/OIC-02-Patrimoni-destinati.md` |
| OIC 4 | Fusione e scissione | `md/OIC-04-Fusione-e-scissione.md` |
| OIC 5 | Bilanci di liquidazione | `md/OIC-05-Bilanci-di-liquidazione.md` |
| OIC 8 | Le quote di emissione di gas ad effetto serra | `md/OIC-08-Quote-emissione-gas-serra.md` |
| OIC 9 | Svalutazioni per perdite durevoli | `md/OIC-09-Svalutazioni-perdite-durevoli.md` |
| OIC 10 | Rendiconto finanziario | `md/OIC-10-Rendiconto-finanziario.md` |
| OIC 11 | Finalità e postulati del bilancio d'esercizio | `md/OIC-11-Postulati.md` |
| OIC 12 | Composizione e schemi del bilancio | `md/OIC-12-Composizione-schemi-bilancio.md` |
| OIC 13 | Rimanenze | `md/OIC-13-Rimanenze.md` |
| OIC 14 | Disponibilità liquide | `md/OIC-14-Disponibilita-liquide.md` |
| OIC 15 | Crediti | `md/OIC-15-Crediti.md` |
| OIC 16 | Immobilizzazioni materiali | `md/OIC-16-Immobilizzazioni-materiali.md` |
| OIC 17 | Bilancio consolidato e metodo del patrimonio netto | `md/OIC-17-Bilancio-consolidato-metodo-PN.md` |
| OIC 18 | Ratei e risconti | `md/OIC-18-Ratei-e-risconti.md` |
| OIC 19 | Debiti | `md/OIC-19-Debiti.md` |
| OIC 20 | Titoli di debito | `md/OIC-20-Titoli-di-debito.md` |
| OIC 21 | Partecipazioni | `md/OIC-21-Partecipazioni.md` |
| OIC 23 | Lavori in corso su ordinazione | `md/OIC-23-Lavori-in-corso-su-ordinazione.md` |
| OIC 24 | Immobilizzazioni immateriali | `md/OIC-24-Immobilizzazioni-immateriali.md` |
| OIC 25 | Imposte sul reddito | `md/OIC-25-Imposte-sul-reddito.md` |
| OIC 26 | Operazioni, attività e passività in valuta estera | `md/OIC-26-Operazioni-valuta-estera.md` |
| OIC 28 | Patrimonio netto | `md/OIC-28-Patrimonio-netto.md` |
| OIC 29 | Cambiamenti di principi contabili | `md/OIC-29-Cambiamenti-principi-contabili.md` |
| OIC 30 | I bilanci intermedi | `md/OIC-30-Bilanci-intermedi.md` |
| OIC 31 | Fondi per rischi e oneri e TFR | `md/OIC-31-Fondi-rischi-oneri-TFR.md` |
| OIC 32 | Strumenti finanziari derivati | `md/OIC-32-Strumenti-finanziari-derivati.md` |
| OIC 33 | Passaggio ai principi contabili nazionali | `md/OIC-33-Passaggio-principi-contabili-nazionali.md` |
| OIC 34 | Ricavi | `md/OIC-34-Ricavi.md` |
| OIC 35 | ETS (sistema di scambio quote di emissione) | `md/OIC-35-ETS.md` |

## Aggiornamento

Questa raccolta è uno snapshot statico (scaricato il 7 giugno 2026). L'OIC pubblica periodicamente emendamenti — alcuni principi (OIC 13, 16, 24, 25, 31) avranno modifiche applicabili dai bilanci 2026. Per verificare se ci sono versioni più recenti, ricontrollare la pagina [fondazioneoic.eu/principi-contabili-category/2025/](https://www.fondazioneoic.eu/principi-contabili-category/2025/) e ri-eseguire lo scaricamento/conversione.
