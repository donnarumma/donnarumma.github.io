# donnarumma.github.io

Sito personale di **Francesco Donnarumma**. Replica statica e modificabile offline
del [sito Google Sites](https://www.francescodonnarumma.net/), importato il
14 settembre 2026.

Repository: <https://github.com/donnarumma/donnarumma.github.io>.
Cartella locale: `CurriculumVitae/Website`, con un proprio `.git`, indipendente
dal repository del CV. Nessun materiale di Sara Di Costanzo e' incluso.

## Aprire Il Sito

Aprire [index.html](index.html) nel browser. Non servono server, Node, npm,
Google Sites o connessione Internet. I file HTML gia' generati sono inclusi.

Sono locali pagine, ricerca, filtri, immagini, GIF, font, CV e bibliografia.
I collegamenti a editori, profili e video YouTube richiedono Internet quando
vengono aperti; non vengono caricati iframe o tracker in background.

## Modificare I Contenuti

| File | Contenuto |
| --- | --- |
| [content/site.json](content/site.json) | Testi delle sei pagine, 70 voci bibliografiche, immagini, highlights e video. |
| [content/settings.json](content/settings.json) | Contatti, profili aggiuntivi, URL pubblico e indicizzazione. |
| [assets/css/site.css](assets/css/site.css) | Impaginazione, colori e versioni desktop/mobile. |
| [templates/base.html](templates/base.html) | Struttura comune, navigazione, metadati e ricerca. |
| [assets/images/](assets/images/) | Immagini originali e animazioni conservate localmente. |
| [assets/downloads/](assets/downloads/) | Copie pubblicabili del CV PDF e del BibTeX canonico. |

In `content/site.json`, cercare il titolo o il testo da modificare. Ogni voce di
`pages.papers.entries` ha un `id` stabile, un `year` per il filtro e una lista
`paragraphs` con testo/HTML semplice (`strong`, `em`, `a`, `br`). Si possono usare
normalmente lettere accentate UTF-8. L'ordine nell'array e' l'ordine nella pagina.
Per aggiungere una voce usare un nuovo ID, senza rinumerare le vecchie ancore.
Il campo facoltativo `title` permette di specificare il titolo nella ricerca.

Dalla cartella `Website`, dopo le modifiche:

```bash
python3 tools/build.py
python3 tools/check.py
```

Servono solo Python 3 e la sua libreria standard. Non modificare direttamente
gli `index.html` o `assets/js/search-index.js`: vengono rigenerati.

Per aggiornare esplicitamente i due download dal CV nella cartella superiore:

```bash
python3 tools/sync_cv.py
python3 tools/build.py
python3 tools/check.py
```

La sincronizzazione copia solo PDF e BibTeX: non riscrive automaticamente la
pagina Papers, che conserva anche tesi, interventi e contributi presenti nel
sito storico ma non necessariamente nel BibTeX. Nessuna modifica ai CV originali.

## Verifiche

`tools/check.py` controlla file, link interni, ancore, conteggio delle voci,
assenza di dipendenze remote e integrita' delle immagini originali.

Il test opzionale `tools/browser_check.py` verifica Chromium a cinque larghezze,
con Internet bloccato: immagini, font, ricerca, filtri e navigazione mobile.
Richiede `websockets` e un browser dedicato con CDP sulla porta 9334.

```bash
chromium --headless=new --disable-gpu --remote-debugging-port=9334 --user-data-dir=/tmp/francesco-website-test about:blank
```

In un altro terminale:

```bash
python3 tools/browser_check.py
```

Risultati e screenshot in `.local/checks/`, esclusi da Git e dalla pubblicazione.
Arrestare il browser di test al termine. Il controllo statico non certifica la
disponibilita' attuale di tutti i vecchi link verso editori e servizi esterni.

## Pubblicazione

Il codice e' versionato nel repository GitHub indicato sopra. La pubblicazione
del **sito su GitHub Pages non e' stata attivata**: caricare i file su GitHub
e avviare il deploy sono due operazioni distinte. Google Sites e DNS restano
invariati. Nessun dominio personalizzato e' stato attivato.

Il workflow [Publish Website (Manual)](.github/workflows/pages.yml) si avvia
soltanto manualmente, non a ogni push. Pubblica solo HTML e `assets`, non i
sorgenti, le note di migrazione o la cache locale.

Procedura e punti da rivedere prima del passaggio:
[migration/README.md](migration/README.md).

## Provenienza E Licenze

I contenuti e le immagini provengono dal sito personale esistente. Questo
repository non concede una licenza generale sui testi, sulle immagini o sui
marchi di terzi. I loghi identificano i rispettivi servizi.

- Lato e Pacifico: licenze OFL incluse in `assets/fonts/`.
- Lucide 0.468.0: licenza ISC inclusa in `assets/vendor/Lucide-LICENSE`.
- OpenAlex: [simbolo ufficiale bianco](https://github.com/ourresearch/openalex-gui/blob/master/public/brand-assets/openalex-mark-white.png),
  introdotto nel [nuovo marchio](https://blog.openalex.org/a-new-logo-for-openalex/),
  conservato in PNG a 526 x 526 pixel e visualizzato piu' piccolo degli altri loghi.
- [migration/assets.json](migration/assets.json): URL originali, dimensioni,
  numero di fotogrammi e hash SHA-256.
- [migration/cv-snapshot.json](migration/cv-snapshot.json): provenienza dei download.

`tools/import_google_site.py` e' uno strumento di **prima importazione**, non di
sincronizzazione quotidiana. Richiede BeautifulSoup/Pillow e puo' richiedere la
cache del browser per i file Google. Si rifiuta di sovrascrivere i contenuti
esistenti senza `--overwrite`: non rieseguirlo sui testi gia' modificati.
